#!/usr/bin/env python3

import collections
import re
import sys

DEBUG = False
def debug(msg):
    if DEBUG:
        print(msg)

class RxLowPulse(Exception):
    pass

class Module:

    def __init__(self, name, outputs):
        self.name = name
        self.outputs = outputs

    def process_pulse(self, _):
        return []

class RXModule:

    def __init__(self, name, outputs):
        self.name = name
        self.outputs = outputs

    def process_pulse(self, pulse):
        if not pulse.high:
            raise RxLowPulse()
        return []

class Broadcaster:

    def __init__(self, name, outputs):
        self.name = name
        self.outputs = outputs

    def process_pulse(self, pulse):
        ret = []
        for output in self.outputs:
            new_pulse = Pulse(pulse.end, output, high=pulse.high)
            debug(f"(Broadcaster) {pulse.end} - {'high' if new_pulse.high else 'low'}-> {new_pulse.end}")
            ret.append(new_pulse)
        return ret

class Conjunction:

    def __init__(self, name, outputs):
        self.name = name
        self.outputs = outputs
        self.input_states = {}
        self.max_potential_falses = 0

    def reset_states(self):
        """Used for testing"""
        for input in self.input_states:
            self.input_states[input] = False

    def add_input(self, input):
        self.input_states[input] = False
        # self.max_potential_falses += 1

    def process_pulse(self, pulse):
        assert pulse.start in self.input_states

        self.input_states[pulse.start] = pulse.high

        output_state = False
        # if self.max_potential_falses <= 1:
        for input in self.input_states.values():
            if not input:
                output_state = True
                break
        # s = set(self.input_states.values())
        # if len(s) == 1 and next(iter(s)) == True:
        #     # Send a low pulse only if all input states are high (i.e. True)
        #     output_state = False

        ret = []
        for output in self.outputs:
            new_pulse = Pulse(pulse.end, output, high=output_state)
            debug(f"(Conjunction) {pulse.end} - {'high' if new_pulse.high else 'low'}-> {new_pulse.end}")
            ret.append(new_pulse)
        return ret

class FlipFlop:

    def __init__(self, name, outputs):
        self.name = name
        self.outputs = outputs
        self.state = False

    def reset_states(self):
        """Used for testing"""
        self.state = False

    def process_pulse(self, pulse):
        if pulse.high:
            return []
        ret = []
        for output in self.outputs:
            new_pulse = Pulse(pulse.end, output, high=not self.state)
            debug(f"(FlipFlop) {pulse.end} - {'high' if new_pulse.high else 'low'}-> {new_pulse.end}")
            ret.append(new_pulse)
        self.state = not self.state
        return ret

class Pulse:

    def __init__(self, start, end, high):
        self.start = start
        self.end = end
        self.high = high
        self.next = None

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end and self.high == other.high

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.start} -> {self.end} ({self.high})"

def parse_input(filename, part2):
    modules = {}
    broadcaster_prog = re.compile("broadcaster -> (.*)")
    named_prog = re.compile("[%&]{1}([a-z]+) -> (.*)")
    with open(filename) as f:
        lines = f.readlines()
    conjunctions = {}
    for line in lines:
        match line[0]:
            case "b":
                m = broadcaster_prog.match(line)
                outputs = [output.strip() for output in m.group(1).split(",")]
                modules["broadcaster"] = Broadcaster("broadcaster", outputs)
            case "&":
                m = named_prog.match(line)
                name = m.group(1)
                outputs = [output.strip() for output in m.group(2).split(",")]
                conjunction = Conjunction(name, outputs)
                modules[name] = conjunction
                conjunctions[name] = conjunction
            case "%":
                m = named_prog.match(line)
                name = m.group(1)
                outputs = [output.strip() for output in m.group(2).split(",")]
                modules[name] = FlipFlop(name, outputs)
            case _:
                raise ValueError(f"Unknown module type {line}")
        for output in outputs:
            if output not in modules:
                if part2 and output == "rx":
                    print(f"Adding RXModule")
                    modules[output] = RXModule(output, [])
                else:
                    debug(f"Adding terminal module {output}")
                    modules[output] = Module(output, [])

    for conjunction_name, conjunction in conjunctions.items():
        for dependency_name, module in modules.items():
            if conjunction_name in module.outputs:
                conjunction.add_input(dependency_name)

    return modules


test_conj = Conjunction("conj", ["a", "b"])
test_conj.add_input("x")
assert test_conj.process_pulse(Pulse("x", "conj", high=True)) == [Pulse("conj", "a", high=False), Pulse("conj", "b", high=False)]
test_conj.reset_states()
assert test_conj.process_pulse(Pulse("x", "conj", high=False)) == [Pulse("conj", "a", high=True), Pulse("conj", "b", high=True)]

test_conj.add_input("y")
test_conj.reset_states()
assert test_conj.process_pulse(Pulse("x", "conj", high=True)) == [Pulse("conj", "a", high=True), Pulse("conj", "b", high=True)]
assert test_conj.process_pulse(Pulse("y", "conj", high=True)) == [Pulse("conj", "a", high=False), Pulse("conj", "b", high=False)]
assert test_conj.process_pulse(Pulse("y", "conj", high=True)) == [Pulse("conj", "a", high=False), Pulse("conj", "b", high=False)]
assert test_conj.process_pulse(Pulse("x", "conj", high=True)) == [Pulse("conj", "a", high=False), Pulse("conj", "b", high=False)]
assert test_conj.process_pulse(Pulse("x", "conj", high=False)) == [Pulse("conj", "a", high=True), Pulse("conj", "b", high=True)]
assert test_conj.process_pulse(Pulse("y", "conj", high=False)) == [Pulse("conj", "a", high=True), Pulse("conj", "b", high=True)]

test_ff = FlipFlop("ff", ["a", "b"])
assert test_ff.process_pulse(Pulse("x", "ff", high=True)) == []
assert test_ff.process_pulse(Pulse("x", "ff", high=False)) == [Pulse("ff", "a", high=True), Pulse("ff", "b", high=True)]
assert test_ff.process_pulse(Pulse("x", "ff", high=False)) == [Pulse("ff", "a", high=False), Pulse("ff", "b", high=False)]
test_ff.reset_states()
assert test_ff.process_pulse(Pulse("x", "ff", high=False)) == [Pulse("ff", "a", high=True), Pulse("ff", "b", high=True)]
assert test_ff.process_pulse(Pulse("x", "ff", high=True)) == []
assert test_ff.process_pulse(Pulse("x", "ff", high=False)) == [Pulse("ff", "a", high=False), Pulse("ff", "b", high=False)]

def push_button(pulse_count, modules):
    current_pulses = collections.deque()

    # Add one pulse for the initial button push
    pulse_count[False] += 1
    current_pulses.append(Pulse('button', 'broadcaster', high=False))

    rx_pulse_count = 0
    while len(current_pulses) > 0:
        current_pulse = current_pulses.popleft()
        module = modules[current_pulse.end]

        try:
            new_pulses = module.process_pulse(current_pulse)
        except RxLowPulse as _:
            print("Got RX Pulse")
            rx_pulse_count += 1
            new_pulses = []

        for new_pulse in new_pulses:
            pulse_count[new_pulse.high] += 1
        current_pulses.extend(new_pulses)

    if rx_pulse_count == 1:
        raise RxLowPulse()

    # print(f"Low pulses: {pulse_count[False]}")
    # print(f"High pulses: {pulse_count[True]}")
    # sys.exit

def answer(filename, part2=False):
    modules = parse_input(filename, part2)

    pulse_count = {
        True: 0,
        False: 0
    }

    if part2:
        button_pushes = sys.maxsize
    else:
        button_pushes = 1000

    for i in range(button_pushes):
        if i % 10000 == 0:
            print(f"Button push {i}")
        try:
            push_button(pulse_count, modules)
        except RxLowPulse as _:
            print(f"Hit Rx node at button push {i}")
            return i

    debug(f"Low pulses: {pulse_count[False]}")
    debug(f"High pulses: {pulse_count[True]}")
    return pulse_count[False] * pulse_count[True]

# assert answer("test_input1.txt") == 32000000
# assert answer("test_input2.txt") == 11687500
# assert answer("real_input.txt") == 869395600
print(answer("real_input.txt", part2=True))
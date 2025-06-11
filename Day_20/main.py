#!/usr/bin/env python3

import graphviz
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

    def __str__(self):
        return f"{self.name}"

    def process_pulse(self, pulse, end_pulse):
        return pulse, end_pulse

class RXModule:

    def __init__(self, name, outputs):
        self.name = name
        self.outputs = outputs

    def __str__(self):
        return f"{self.name}"

    def process_pulse(self, pulse, end_pulse):
        if not pulse.high:
            raise RxLowPulse()
        return pulse, end_pulse

class Broadcaster:

    def __init__(self, name, outputs):
        self.name = name
        self.outputs = outputs

    def __str__(self):
        return f"{self.name}"

    def process_pulse(self, pulse, end_pulse):
        for output in self.outputs:
            end_pulse.next = Pulse(pulse.end.name, output, high=pulse.high)
            debug(f"(Broadcaster) {pulse.end} - {'high' if end_pulse.next.high else 'low'}-> {end_pulse.next.end}")
            end_pulse = end_pulse.next
        return pulse, end_pulse

class Conjunction:

    def __init__(self, name, outputs):
        self.name = name
        self.outputs = outputs
        self.input_states = {}
        self.max_potential_falses = 0
        self.input_state_values = []

    def reset_states(self):
        """Used for testing"""
        for input in self.input_states:
            self.input_state_values[self.input_states[input]] = False

    def add_input(self, input):
        self.input_states[input] = len(self.input_state_values)
        self.input_state_values.append(False)

    def __str__(self):
        return f"{self.name}"

    def process_pulse(self, pulse, end_pulse):
        self.input_state_values[self.input_states[pulse.start]] = pulse.high

        output_state = False
        for input in self.input_state_values:
            if not input:
                output_state = True
                break

        for output in self.outputs:
            end_pulse.next = Pulse(pulse.end.name, output, high=output_state)
            debug(f"(Conjunction) {pulse.end} - {'high' if end_pulse.next.high else 'low'}-> {end_pulse.next.end}")
            end_pulse = end_pulse.next

        return pulse, end_pulse

    def xprocess_pulse(self, pulse, end_pulse):
        self.input_states[pulse.start] = pulse.high

        output_state = False
        for input in self.input_states.values():
            if not input:
                output_state = True
                break

        for output in self.outputs:
            end_pulse.next = Pulse(pulse.end.name, output, high=output_state)
            debug(f"(Conjunction) {pulse.end} - {'high' if end_pulse.next.high else 'low'}-> {end_pulse.next.end}")
            end_pulse = end_pulse.next

        return pulse, end_pulse

class FlipFlop:

    def __init__(self, name, outputs):
        self.name = name
        self.outputs = outputs
        self.state = False

    def __str__(self):
        return f"{self.name}"

    def reset_states(self):
        """Used for testing"""
        self.state = False

    def process_pulse(self, pulse, end_pulse):
        if pulse.high:
            return pulse, end_pulse

        self.state = not self.state

        for output in self.outputs:
            end_pulse.next = Pulse(pulse.end.name, output, high=self.state)
            debug(f"(FlipFlop) {pulse.end} - {'high' if end_pulse.next.high else 'low'}-> {end_pulse.next.end}")
            end_pulse = end_pulse.next

        return pulse, end_pulse

class Pulse:

    def __init__(self, start, end, high):
        if type(start) != str:
            raise ValueError(f"start must be a string, not {type(start)}")
        if type(end) == str:
            raise ValueError(f"end must be a Module, not a string")

        self.start = start
        self.end = end
        self.high = high
        self.next = None
        self.module = None

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
                # if part2 and output == "rx":
                #     print(f"Adding RXModule")
                #     modules[output] = RXModule(output, [])
                # else:
                #     debug(f"Adding terminal module {output}")
                modules[output] = Module(output, [])

    for conjunction_name, conjunction in conjunctions.items():
        for dependency_name, module in modules.items():
            if conjunction_name in module.outputs:
                conjunction.add_input(dependency_name)

    for name, module in modules.items():
        module.outputs = [modules[output] for output in module.outputs]

    return modules

def dump_pulse_chain(pulse):
    current_pulse = pulse
    indent = ""
    while current_pulse is not None:
        print(f"{indent}{current_pulse}")
        indent += "  "
        current_pulse = current_pulse.next

def assert_next_pulses(pair, next_pulses):
    pulse, _ = pair
    current_pulse = pulse.next
    for next_pulse in next_pulses:
        if current_pulse != next_pulse:
            print(f"Expected {next_pulse} but got {current_pulse}")
            print(dump_pulse_chain(pulse))
            assert False
        current_pulse = current_pulse.next
    assert current_pulse is None

def dupe(pulse):
    return pulse, pulse

# test_conj = Conjunction("conj", ["a", "b"])
# test_conj.add_input("x")
# assert_next_pulses(test_conj.process_pulse(*dupe(Pulse("x", "conj", high=True))), [Pulse("conj", "a", high=False), Pulse("conj", "b", high=False)])

# test_conj.reset_states()
# assert_next_pulses(test_conj.process_pulse(*dupe(Pulse("x", "conj", high=False))), [Pulse("conj", "a", high=True), Pulse("conj", "b", high=True)])

# test_conj.add_input("y")
# test_conj.reset_states()

# assert_next_pulses(test_conj.process_pulse(*dupe(Pulse("x", "conj", high=True))), [Pulse("conj", "a", high=True), Pulse("conj", "b", high=True)])
# assert_next_pulses(test_conj.process_pulse(*dupe(Pulse("y", "conj", high=True))), [Pulse("conj", "a", high=False), Pulse("conj", "b", high=False)])
# assert_next_pulses(test_conj.process_pulse(*dupe(Pulse("y", "conj", high=True))), [Pulse("conj", "a", high=False), Pulse("conj", "b", high=False)])
# assert_next_pulses(test_conj.process_pulse(*dupe(Pulse("x", "conj", high=True))), [Pulse("conj", "a", high=False), Pulse("conj", "b", high=False)])
# assert_next_pulses(test_conj.process_pulse(*dupe(Pulse("x", "conj", high=False))), [Pulse("conj", "a", high=True), Pulse("conj", "b", high=True)])
# assert_next_pulses(test_conj.process_pulse(*dupe(Pulse("y", "conj", high=False))), [Pulse("conj", "a", high=True), Pulse("conj", "b", high=True)])

# test_ff = FlipFlop("ff", ["a", "b"])
# assert_next_pulses(test_ff.process_pulse(*dupe(Pulse("x", "ff", high=True))), [])
# assert_next_pulses(test_ff.process_pulse(*dupe(Pulse("x", "ff", high=False))), [Pulse("ff", "a", high=True), Pulse("ff", "b", high=True)])
# assert_next_pulses(test_ff.process_pulse(*dupe(Pulse("x", "ff", high=False))), [Pulse("ff", "a", high=False), Pulse("ff", "b", high=False)])
# test_ff.reset_states()
# assert_next_pulses(test_ff.process_pulse(*dupe(Pulse("x", "ff", high=False))), [Pulse("ff", "a", high=True), Pulse("ff", "b", high=True)])
# assert_next_pulses(test_ff.process_pulse(*dupe(Pulse("x", "ff", high=True))), [])
# assert_next_pulses(test_ff.process_pulse(*dupe(Pulse("x", "ff", high=False))), [Pulse("ff", "a", high=False), Pulse("ff", "b", high=False)])

def push_button(pulse_count, modules):
    # Add one pulse for the initial button push
    current_pulse = Pulse('button', modules['broadcaster'], high=False)
    end_pulse = current_pulse

    rx_pulse_count = 0
    while current_pulse is not None:
        # pulse_count[current_pulse.high] += 1
        # module = modules[current_pulse.end]

        try:
            _, end_pulse = current_pulse.end.process_pulse(current_pulse, end_pulse)
        except RxLowPulse as _:
            print("Got RX Pulse")
            rx_pulse_count += 1

        current_pulse = current_pulse.next

    if rx_pulse_count == 1:
        raise RxLowPulse()
    elif rx_pulse_count > 1:
        print(f"Got {rx_pulse_count} RX Pulses")

    # print(f"Low pulses: {pulse_count[False]}")
    # print(f"High pulses: {pulse_count[True]}")
    # sys.exit()

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

    try:
        for i in range(button_pushes):
            if i % 10000 == 0:
                print(f"Button push {i}")
            push_button(pulse_count, modules)
    except RxLowPulse as _:
        print(f"Hit Rx node at button push {i}")
        return i

    debug(f"Low pulses: {pulse_count[False]}")
    debug(f"High pulses: {pulse_count[True]}")
    return pulse_count[False] * pulse_count[True]

modules = parse_input("real_input.txt", part2=True)

def iterate_subtree_until_condition(initial_pulse, final_node, final_node_high):
    button_count = 0
    while 1:
        button_count += 1
        # if button_count % 10000 == 0:
            # print(f"Button push {button_count}")
        current_pulse = initial_pulse
        end_pulse = current_pulse
        hit_count = 0
        while current_pulse is not None:
            if current_pulse.end.name == final_node and current_pulse.high == final_node_high:
                hit_count += 1

            _, end_pulse = current_pulse.end.process_pulse(current_pulse, end_pulse)
            current_pulse = current_pulse.next

        if hit_count == 1:
            print(f"Hit count {hit_count} at button push {button_count}")
            # return button_count
        elif hit_count > 1:
            print(f"Hit count {hit_count} at button push {button_count}")

# iterate_subtree_until_condition(Pulse('broadcaster', modules['ss'], high=False), 'ph', True)
# iterate_subtree_until_condition(Pulse('broadcaster', modules['vq'], high=False), 'tx', True)
# iterate_subtree_until_condition(Pulse('broadcaster', modules['qg'], high=False), 'nz', True)
# iterate_subtree_until_condition(Pulse('broadcaster', modules['kb'], high=False), 'dd', True)




# assert answer("test_input1.txt") == 32000000
# assert answer("test_input2.txt") == 11687500
# assert answer("real_input.txt") == 869395600
# print(f"Answer: {answer('real_input.txt', part2=True)}")

# dot = graphviz.Digraph('round-table', comment='The Round Table')


# for name, module in modules.items():
#     n = name
#     if isinstance(module, Conjunction):
#         n = f"&{name}"
#     elif isinstance(module, FlipFlop):
#         n = f"%{name}"
#     dot.node(name, n)

# for name, module in modules.items():
#     for output in module.outputs:
#         # n = name
#         # if isinstance(module, Conjunction):
#         #     n = f"&{name}"
#         # elif isinstance(module, FlipFlop):
#         #     n = f"%{name}"
#         dot.edge(name, output.name)

# dot.render(directory='doctest-output').replace('\\', '/')




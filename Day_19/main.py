#!/usr/bin/env python3
import copy
import re
import sys

#px{a<2006:qkq,m>2090:A,rfg}
workflow_prog = re.compile("([a-z]+){(.*)}")
instruction_prog = re.compile("([xmas]{1})([<>]{1})(\d+)")
part_prog = re.compile("([xmas]{1})=(\d+)")

class XmasRange:

    def __init__(self, next_instruction, x=(1, 4000), m=(1, 4000), a=(1, 4000), s=(1, 4000)):
        self.next_instruction = next_instruction
        # Ranges are closed intervals
        self.x = x
        self.m = m
        self.a = a
        self.s = s

    def clone(self, new_instruction):
        ret = copy.deepcopy(self)
        ret.next_instruction = new_instruction
        return ret

    def distinct_combinations(self):
        def range_length(r):
            return r[1] - r[0] + 1
        return range_length(self.x) * range_length(self.m) * range_length(self.a) * range_length(self.s)

    def __eq__(self, other):
        return self.next_instruction == other.next_instruction and \
            self.x == other.x and \
            self.m == other.m and \
            self.a == other.a and \
            self.s == other.s

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.next_instruction}: x={self.x}, m={self.m}, a={self.a}, s={self.s}"

class Instruction:

    def __init__(self, string):
        self.raw = string
        self.parse_instruction(string)

    def parse_instruction(self, string):
        # TODO: This was lazy. Should have had a factory to produce different types of instructions.
        if ":" not in string:
            self.value = string
            self.is_const = True
            return
        self.is_const = False
        rest, self.result_if_true = string.split(":")
        m = instruction_prog.match(rest)
        self.category = m.group(1)
        self.comparison = m.group(2)
        self.value = int(m.group(3))

    def evaluate(self, part):
        if self.is_const:
            return self.value
        if self.comparison == "<":
            if part[self.category] < self.value:
                return self.result_if_true
            else:
                return None
        else:
            if part[self.category] > self.value:
                return self.result_if_true
            else:
                return None

    def evaluate_range(self, xmas_range):
        if self.is_const:
            return [xmas_range.clone(self.value)]
        range_for_category = getattr(xmas_range, self.category)
        if self.comparison == "<":
            if self.value > range_for_category[1]:
                # We get evertyhing
                #---[-----]---
                #----------v--
                return [xmas_range.clone(self.result_if_true)]
            elif self.value <= range_for_category[0]:
                # We get nothing
                #---[-----]---
                #---v---------
                return [xmas_range.clone(None)]
            else:
                # We get a split range
                #---[-----]---
                #------v------
                left_range = xmas_range.clone(self.result_if_true)
                setattr(left_range, self.category, (range_for_category[0], self.value - 1))
                rigth_range = xmas_range.clone(None)
                setattr(rigth_range, self.category, (self.value, range_for_category[1]))
                return [left_range, rigth_range]
        else: # self.comparison == ">":
            if self.value < range_for_category[0]:
                # We get evertyhing
                #---[-----]---
                #--v----------
                return [xmas_range.clone(self.result_if_true)]
            elif self.value >= range_for_category[1]:
                # We get nothing
                #---[-----]---
                #---------v---
                return [xmas_range.clone(None)]
            else:
                # We get a split range
                #---[-----]---
                #------v------
                left_range = xmas_range.clone(None)
                setattr(left_range, self.category, (range_for_category[0], self.value))
                rigth_range = xmas_range.clone(self.result_if_true)
                setattr(rigth_range, self.category, (self.value + 1, range_for_category[1]))
                return [left_range, rigth_range]

assert Instruction("xyz").evaluate({}) == "xyz"
assert Instruction("s>2770:qs").evaluate({"s":2770}) == None
assert Instruction("s>2770:qs").evaluate({"s":2771}) == "qs"
assert Instruction("s<2770:qs").evaluate({"s":2769}) == "qs"
assert Instruction("s<2770:qs").evaluate({"s":2770}) == None

assert Instruction("xyz").evaluate_range(XmasRange("")) == [XmasRange("xyz")]

assert Instruction("s>2770:qs").evaluate_range(XmasRange("")) == [XmasRange(None, s=(1, 2770)), XmasRange("qs", s=(2771, 4000))]
assert Instruction("s<2770:qs").evaluate_range(XmasRange("")) == [XmasRange("qs", s=(1, 2769)), XmasRange(None, s=(2770, 4000))]

assert Instruction("s<1:qs").evaluate_range(XmasRange("")) == [XmasRange(None, s=(1, 4000))]
assert Instruction("s>0:qs").evaluate_range(XmasRange("")) == [XmasRange("qs", s=(1, 4000))]
assert Instruction("s>1:qs").evaluate_range(XmasRange("")) == [XmasRange(None, s=(1, 1)), XmasRange("qs", s=(2, 4000))]

assert Instruction("s<4001:qs").evaluate_range(XmasRange("")) == [XmasRange("qs", s=(1, 4000))]
assert Instruction("s<4000:qs").evaluate_range(XmasRange("")) == [XmasRange("qs", s=(1, 3999)), XmasRange(None, s=(4000, 4000))]
assert Instruction("s>4000:qs").evaluate_range(XmasRange("")) == [XmasRange(None, s=(1, 4000))]

class Workflow:

    def __init__(self, instructions):
        self.instructions = [Instruction(instruction) for instruction in instructions.split(",")]

    def evaluate(self, part):
        for instruction in self.instructions:
            result = instruction.evaluate(part)
            if result is not None:
                return result

        assert f"Failed to evaluate {self} for {part}"

    def evaluate_range(self, xmas_range):
        current_ranges = [xmas_range]
        split_ranges = []
        for instruction in self.instructions:
            new_ranges = []
            for current_range in current_ranges:
                new_ranges += instruction.evaluate_range(current_range)

            ranges_for_next_instruction = []
            for new_range in new_ranges:
                if new_range.next_instruction is not None:
                    split_ranges.append(new_range)
                    continue
                ranges_for_next_instruction.append(new_range)
            current_ranges = ranges_for_next_instruction

        return split_ranges

assert len(Workflow("a<2006:qkq,m>2090:A,rfg").instructions) == 3
assert Workflow("a<2006:qkq,m>2090:A,rfg").evaluate({"a":2005}) == "qkq"
assert Workflow("a<2006:qkq,m>2090:A,rfg").evaluate({"a":2006, "m": 2090}) == "rfg"
assert Workflow("a<2006:qkq,m>2090:A,rfg").evaluate({"a":2091, "m": 2091}) == "A"

# print(Workflow("a<2006:qkq,m>2090:A,rfg").evaluate_range(XmasRange("")))
assert Workflow("a<2006:qkq,m>2090:A,rfg").evaluate_range(XmasRange("")) == [XmasRange("qkq", a=(1, 2005)), XmasRange("A", a=(2006, 4000), m=(2091, 4000)), XmasRange("rfg", a=(2006, 4000), m=(1, 2090))]

def parse_workflow(string):
    m = workflow_prog.match(string)
    return m.group(1), Workflow(m.group(2))

def parse_part(string):
    # {x=410,m=675,a=8,s=1050}
    part = {}
    for assignment in string[1:-1].split(","):
        m = part_prog.match(assignment)
        part[m.group(1)] = int(m.group(2))
    return part

def parse_input(filename):
    workflows = {}
    parts = []
    with open(filename) as f:
        lines = f.readlines()
    for iline, line in enumerate(lines):
        if line.strip() == "":
            break
        name, instructions = parse_workflow(line.strip())
        workflows[name] = instructions

    for jline in range(iline + 1, len(lines)):
        line = lines[jline]
        parts.append(parse_part(line))

    return workflows, parts

# NASA would hate this function!
def part_is_accepted(workflows, part):
    next_workflow = "in"
    while 1:
        match workflows[next_workflow].evaluate(part):
            case "A":
                return True
            case "R":
                return False
            case next_workflow:
                pass

test_workflows = {"in": Workflow("a<2006:R,A")}
assert part_is_accepted(test_workflows, {"a": 2005}) == False
assert part_is_accepted(test_workflows, {"a": 2006}) == True
test_workflows = {"in": Workflow("a<2006:xx,A"), "xx": Workflow("m>10:A,R")}
assert part_is_accepted(test_workflows, {"a": 2006}) == True
assert part_is_accepted(test_workflows, {"a": 2005, "m": 10}) == False
assert part_is_accepted(test_workflows, {"a": 2005, "m": 11}) == True

def answer_part_1(filename):
    workflows, parts = parse_input(filename)
    accepted = []
    for part in parts:
        if part_is_accepted(workflows, part):
            accepted.append(part)
    return sum([sum(part.values()) for part in accepted])

def answer_part_2(filename):
    workflows, _ = parse_input(filename)
    ranges = [XmasRange("in")]
    accepted_ranges = []
    rejected_ranges = []
    while len(ranges) > 0:
        next_ranges = []
        for range_ in ranges:
            split_ranges = workflows[range_.next_instruction].evaluate_range(range_)
            for split_range in split_ranges:
                if split_range.next_instruction == "A":
                    accepted_ranges.append(split_range)
                elif split_range.next_instruction == "R":
                    rejected_ranges.append(split_range)
                else:
                    next_ranges.append(split_range)

        ranges = next_ranges
    return sum([range_.distinct_combinations() for range_ in accepted_ranges])

assert answer_part_1("test_input.txt") == 19114
assert answer_part_1("real_input.txt") == 368964
assert answer_part_2("test_input.txt") == 167409079868000
print(answer_part_2("real_input.txt"))

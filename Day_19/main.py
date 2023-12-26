#!/usr/bin/env python3
import re
import sys

#px{a<2006:qkq,m>2090:A,rfg}
workflow_prog = re.compile("([a-z]+){(.*)}")
instruction_prog = re.compile("([xmas]{1})([<>]{1})(\d+)")
part_prog = re.compile("([xmas]{1})=(\d+)")

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

assert Instruction("xyz").evaluate({}) == "xyz"
assert Instruction("s>2770:qs").evaluate({"s":2770}) == None
assert Instruction("s>2770:qs").evaluate({"s":2771}) == "qs"
assert Instruction("s<2770:qs").evaluate({"s":2769}) == "qs"
assert Instruction("s<2770:qs").evaluate({"s":2770}) == None

class Workflow:

    def __init__(self, instructions):
        self.instructions = [Instruction(instruction) for instruction in instructions.split(",")]

    def evaluate(self, part):
        for instruction in self.instructions:
            result = instruction.evaluate(part)
            if result is not None:
                return result

        assert f"Failed to evaluate {self} for {part}"

assert len(Workflow("a<2006:qkq,m>2090:A,rfg").instructions) == 3
assert Workflow("a<2006:qkq,m>2090:A,rfg").evaluate({"a":2005}) == "qkq"
assert Workflow("a<2006:qkq,m>2090:A,rfg").evaluate({"a":2006, "m": 2090}) == "rfg"
assert Workflow("a<2006:qkq,m>2090:A,rfg").evaluate({"a":2091, "m": 2091}) == "A"

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

# print(parse_input("test_input.txt"))
# assert answer_part_1("test_input.txt") == 19114
print(answer_part_1("real_input.txt"))

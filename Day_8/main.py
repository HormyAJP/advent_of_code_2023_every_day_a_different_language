#!/usr/bin/env python3

import math
import re

def read_input(filename):
    with open(filename) as f:
        lines = [line.strip() for line in f.readlines()]
    rl_instructions = lines[0]
    mappings = {}
    prog = re.compile("^([A-Z0-9]{3}) = \(([A-Z0-9]{3}), ([A-Z0-9]{3})\)$")
    for line in lines[2:]:
        match = prog.match(line)
        if match:
            mappings[match.group(1)] = [match.group(2), match.group(3)]
        else:
            raise Exception(f"Bad line: {line}")
    return rl_instructions, mappings

def all_nodes_are_at_the_end(nodes):
    for node in nodes:
        if node[2] != "Z":
            return False
    return True

# This function was designed as a naive way to process multiple nodes at once. It's not practical
# with the input data. Instead I just call this with one element arrays and use the lcm to
# "aggregate" the results.
def step_to_the_end(current_nodes, rl_instructions, mappings):
    step_count = 0
    while (not all_nodes_are_at_the_end(current_nodes)):
        rl = rl_instructions[step_count % len(rl_instructions)]
        for i, node in enumerate(current_nodes):
            current_nodes[i] = mappings[node][1 if rl == "R" else 0]
        step_count += 1

    return step_count

def answer_part_1(filename):
    rl_instructions, mappings = read_input(filename)
    start_nodes = ["AAA"]
    return step_to_the_end(start_nodes, rl_instructions, mappings)

assert answer_part_1("test_input1.txt") == 2
assert answer_part_1("test_input2.txt") == 6
assert answer_part_1("real_input.txt") == 15871

def answer_part_2(filename):
    rl_instructions, mappings = read_input(filename)
    start_nodes = []
    for key in mappings.keys():
        if key[2] == "A":
            start_nodes.append(key)
    steps_per_node = []
    for node in start_nodes:
        steps_per_node.append(step_to_the_end([node], rl_instructions, mappings))
    return math.lcm(*steps_per_node)

assert answer_part_2("test_input3.txt") == 6
print(f"Answer to part 2 is {answer_part_2('real_input.txt')}")

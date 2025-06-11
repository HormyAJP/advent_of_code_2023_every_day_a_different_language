#!/usr/bin/env python3

import copy
import random

class Node:

    def __init__(self, name):
        self.name = name
        self.next_nodes = []

def parse_input(filename):
    ret = {}
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            left, right = line.split(":")
            rights = right.split()
            if left not in ret:
                ret[left] = []
            ret[left] += rights
            for right in rights:
                if right not in ret:
                    ret[right] = []
                ret[right].append(left)
    return ret

def random_edge(graph):
    keys = list(graph.keys())
    left = keys[random.randrange(len(keys))]
    rights = graph[left]
    right = rights[random.randrange(len(rights))]
    return left, right

def contract(graph, left, right):
    lefts_next_nodes = graph[left]
    lefts_next_nodes = list(filter((right).__ne__, lefts_next_nodes))
    del graph[left]
    rights_next_nodes = graph[right]
    rights_next_nodes = list(filter((left).__ne__, rights_next_nodes))
    del graph[right]

    newnode = f"{left},{right}"
    assert newnode not in graph

    for node in lefts_next_nodes:
        graph[node] = [x if x != left else newnode for x in graph[node]]

    for node in rights_next_nodes:
        graph[node] = [x if x != right else newnode for x in graph[node]]

    graph[newnode] = lefts_next_nodes + rights_next_nodes

def karger(graph):
    while len(graph) > 2:
        left, right = random_edge(graph)
        # print(f"Contracting {left} and {right}")
        contract(graph, left, right)

def repeat_karger(graph):
    while 1:
        graph_copy = copy.deepcopy(graph)
        karger(graph_copy)
        rights = next(iter(graph_copy.values()))
        if len(rights) == 3:
            return graph_copy
        # print(f"Karger failed. We ended up with {len(rights)} edges connecting the last two nodes")

def answer_part1(filename):
    graph = parse_input(filename)
    contracted_graph = repeat_karger(graph)
    two_keys = list(contracted_graph.keys())
    return (two_keys[0].count(",") + 1) * (two_keys[1].count(",") + 1 )

assert answer_part1("test_input.txt") == 54
print(answer_part1("real_input.txt"))
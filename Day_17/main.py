#!/usr/bin/env python3

import numpy as np
import os
import functools
import sys
from enum import Enum

def parse_input(filename):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)) as f:
        rows = []
        for line in f.readlines():
            rows.append([int(val) for val in list(line.strip())])
        return np.array(rows)

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

# def dump_list_of_nodes(nodes, grid):
#     return dump_list_of_indices([(node.index[0], node.index[1]) for node in nodes], grid)

# def dump_list_of_indices(indices, grid):
#     pretty = np.full_like(grid, "░", dtype=object)
#     for index in indices:
#         index = (index[0], index[1])
#         pretty[index] = "█"
#     for row in pretty:
#         print(" ".join(row))

# def dump_head_of_paths(paths, grid):
#     heads = [(path[-1], path.heat_loss) for path in paths]
#     pretty = np.full_like(grid, "░░░", dtype=object)
#     for index, heat_loss in heads:
#         pretty[index] = str(heat_loss).zfill(3)
#     for row in pretty:
#         print(" ".join(row))

class Node:
    def __init__(self, weight, index):
        self.weight = weight
        self.index = index
        self.visited = False
        self.min_distance = np.inf
        self.next_nodes = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{(self.index[0], self.index[1], integer_to_direction_and_count(self.index[2], 3))}: w={self.weight}, d={self.min_distance}, v={self.visited}"

def direction_and_count_to_integer(direction, count, max_steps):
    assert 0 < count <= max_steps
    return direction.value * max_steps + (count - 1)

def integer_to_direction_and_count(value, max_steps):
    return (Direction(value // max_steps), value % max_steps + 1)

assert direction_and_count_to_integer(*integer_to_direction_and_count(0, 3), 3) == 0
assert direction_and_count_to_integer(*integer_to_direction_and_count(1, 3), 3) == 1
assert direction_and_count_to_integer(*integer_to_direction_and_count(2, 3), 3) == 2
assert direction_and_count_to_integer(*integer_to_direction_and_count(3, 3), 3) == 3
assert direction_and_count_to_integer(*integer_to_direction_and_count(4, 3), 3) == 4
assert direction_and_count_to_integer(*integer_to_direction_and_count(5, 3), 3) == 5
assert direction_and_count_to_integer(*integer_to_direction_and_count(6, 3), 3) == 6
assert integer_to_direction_and_count(direction_and_count_to_integer(Direction.UP, 1, 3), 3) == (Direction.UP, 1)
assert integer_to_direction_and_count(direction_and_count_to_integer(Direction.UP, 2, 3), 3) == (Direction.UP, 2)
assert integer_to_direction_and_count(direction_and_count_to_integer(Direction.UP, 3, 3), 3) == (Direction.UP, 3)
assert integer_to_direction_and_count(direction_and_count_to_integer(Direction.RIGHT, 1, 3), 3) == (Direction.RIGHT, 1)
assert integer_to_direction_and_count(direction_and_count_to_integer(Direction.RIGHT, 2, 3), 3) == (Direction.RIGHT, 2)
assert integer_to_direction_and_count(direction_and_count_to_integer(Direction.RIGHT, 3, 3), 3) == (Direction.RIGHT, 3)

def is_inside_grid(shape, index):
    if index[0] < 0 or index[1] < 0:
        return False
    if index[0] >= shape[0] or index[1] >= shape[1]:
        return False
    return True

def next_possible_indices_for_regular_crucible(grid_shape, i, j, k):
    direction, count = integer_to_direction_and_count(k, 3)
    ret = move_left_and_right((i, j), direction, 3)
    if count < 3:
        ret += move_forward((i, j), direction, count, 3)
    return ret

# TODO: Make mim-steps variable
def is_room_for_minimum_steps(grid_shape, index):
    direction, count = integer_to_direction_and_count(index[2], 10)
    # print(f"is_room_for_minimum_steps: {index}, {direction}, {count}")
    assert count == 1
    match direction:
        case Direction.UP:
            if index[0] - 3 < 0:
                # print("No room up")
                return False
        case Direction.RIGHT:
            if index[1] + 3 >= grid_shape[1]:
                # print("No room right")
                return False
        case Direction.DOWN:
            if index[0] + 3 >= grid_shape[0]:
                # print("No room down")
                return False
        case Direction.LEFT:
            if index[1] - 3 < 0:
                # print("No room left")
                return False
        case _:
            raise Exception("Unknown direction")
    return True

assert not is_room_for_minimum_steps((10, 20), (0, 0, direction_and_count_to_integer(Direction.UP, 1, 10)))
assert not is_room_for_minimum_steps((10, 20), (1, 0, direction_and_count_to_integer(Direction.UP, 1, 10)))
assert not is_room_for_minimum_steps((10, 20), (2, 0, direction_and_count_to_integer(Direction.UP, 1, 10)))
assert is_room_for_minimum_steps((10, 20), (3, 0, direction_and_count_to_integer(Direction.UP, 1, 10)))

assert is_room_for_minimum_steps((10, 20), (0, 0, direction_and_count_to_integer(Direction.RIGHT, 1, 10)))
assert not is_room_for_minimum_steps((10, 20), (0, 19, direction_and_count_to_integer(Direction.RIGHT, 1, 10)))
assert not is_room_for_minimum_steps((10, 20), (0, 18, direction_and_count_to_integer(Direction.RIGHT, 1, 10)))
assert not is_room_for_minimum_steps((10, 20), (0, 17, direction_and_count_to_integer(Direction.RIGHT, 1, 10)))
assert is_room_for_minimum_steps((10, 20), (0, 16, direction_and_count_to_integer(Direction.RIGHT, 1, 10)))
# exit()

def next_possible_indices_for_ultra_crucible(grid_shape, i, j, k):
    direction, count = integer_to_direction_and_count(k, 10)
    ft = functools.partial(is_room_for_minimum_steps, grid_shape)
    if count < 4:
        # We MUST move forward in this case
        return move_forward((i, j), direction, count, 10)
    elif 4 <= count < 10:
        # We are allowed to move left, right and forward
        indices = move_left_and_right((i, j), direction, 10)
        indices = list(filter(ft, indices))
        return indices + move_forward((i, j), direction, count, 10)
    elif count == 10:
        # We MUST turn in this case
        indices = move_left_and_right((i, j), direction, 10)
        return list(filter(ft, indices))
    else:
        raise Exception("Logic error")

# TODO: Optimize the whole thing by reducing possibilities for index 0,0. There's a lot of unnecessary
# nodes. This was a result of using a numpy array.
def build_graph(grid, is_ultra_crucible):
    max_steps = 10 if is_ultra_crucible else 3
    nodes = build_nodes(grid, max_steps)

    bounds_filter = functools.partial(is_inside_grid, (nodes.shape[0], nodes.shape[1]))
    next_indices_function = next_possible_indices_for_ultra_crucible if is_ultra_crucible else next_possible_indices_for_regular_crucible

    for i in range(0, nodes.shape[0]):
        for j in range(0, nodes.shape[1]):
            for k in range(0, nodes.shape[2]):
                indices = filter(bounds_filter, next_indices_function(nodes.shape, i, j, k))
                nodes[i, j, k].next_nodes = [nodes[index] for index in indices]

    # Need to give the algo a starting point (top left)
    for node in nodes[0, 0]:
        node.min_distance = 0

    return nodes

def move_left_and_right(index, direction, max_steps):
    indices = []
    match direction:
        case Direction.UP:
            indices.append((index[0], index[1] - 1, direction_and_count_to_integer(Direction.LEFT, 1, max_steps)))
            indices.append((index[0], index[1] + 1, direction_and_count_to_integer(Direction.RIGHT, 1, max_steps)))
        case Direction.RIGHT:
            indices.append((index[0] - 1, index[1], direction_and_count_to_integer(Direction.UP, 1, max_steps)))
            indices.append((index[0] + 1, index[1], direction_and_count_to_integer(Direction.DOWN, 1, max_steps)))
        case Direction.DOWN:
            indices.append((index[0], index[1] - 1, direction_and_count_to_integer(Direction.LEFT, 1, max_steps)))
            indices.append((index[0], index[1] + 1, direction_and_count_to_integer(Direction.RIGHT, 1, max_steps)))
        case Direction.LEFT:
            indices.append((index[0] - 1, index[1], direction_and_count_to_integer(Direction.UP, 1, max_steps)))
            indices.append((index[0] + 1, index[1], direction_and_count_to_integer(Direction.DOWN, 1, max_steps)))
        case unknown:
            raise Exception(f"Unknown direction: {unknown}")

    return indices

# TODO: Use consistent terminology for index
def move_forward(index, direction, current_count, max_steps):
    k = direction_and_count_to_integer(direction, current_count + 1, max_steps)
    match direction:
        case Direction.UP:
            return [(index[0] - 1, index[1], k)]
        case Direction.RIGHT:
            return [(index[0], index[1] + 1, k)]
        case Direction.DOWN:
            return [(index[0] + 1, index[1], k)]
        case Direction.LEFT:
            return [(index[0], index[1] - 1, k)]
        case _:
            raise Exception("Unknown direction")

# Maybe optmize by looking at the leaves
def find_minimal_unvisited_node(nodes, minimal_candidates):
    minimum_value = np.inf
    minimum_node = None
    for node in minimal_candidates:
        if node.visited:
            raise Exception(f"Logic Error: Node {node} in minimal candidates is already visited")
        if node.min_distance < minimum_value:
            minimum_node = node
            minimum_value = node.min_distance

    if minimum_node is None:
        return None

    minimal_candidates.remove(minimum_node)
    for new_node in [node for node in minimum_node.next_nodes if not node.visited]:
        if not new_node.visited and new_node not in minimal_candidates:
            minimal_candidates.append(new_node)

    return minimum_node

def dijkstra(grid, nodes):
    print(f"\ndijkstra with {nodes.size} nodes")
    nodes_done = 0
    minimal_candidates = list(nodes[0, 0])
    while 1:
        if nodes_done % 1000 == 0:
            print(f"Progress: {nodes_done} nodes visited")
        node = find_minimal_unvisited_node(nodes, minimal_candidates)
        if node is None:
            print("No more minimal nodes")
            break
        for next_node in node.next_nodes:
            if next_node.visited:
                continue
            next_node.min_distance = min(next_node.min_distance, node.min_distance + next_node.weight)
        node.visited = True
        nodes_done += 1

def build_nodes(grid, max_steps):
    nodes = np.empty(grid.shape + (max_steps * 4,), dtype=Node)

    # TODO: Is there a neat way to do full_like but produce a copy of the object in each index?
    for i in range(nodes.shape[0]):
        for j in range(nodes.shape[1]):
            for k in range(nodes.shape[2]):
                nodes[i,j,k] = Node(grid[i, j], (i,j,k))

    return nodes

def compute_answer(filename, is_ultra_crucible):
    grid = parse_input(filename)
    nodes = build_graph(grid, is_ultra_crucible)

    dijkstra(grid, nodes)
    ret = min([n.min_distance for n in nodes[-1, -1]])
    print(f"dijkstra done. Min is {ret}")
    return ret

assert compute_answer("test_input.txt", is_ultra_crucible=False) == 102
# Test too slow to run each time
# assert compute_answer("real_input.txt", is_ultra_crucible=False) == 956

assert compute_answer("test_input.txt", is_ultra_crucible=True) == 94
assert compute_answer("test_input2.txt", is_ultra_crucible=True) == 71
print(compute_answer('real_input.txt', is_ultra_crucible=True))

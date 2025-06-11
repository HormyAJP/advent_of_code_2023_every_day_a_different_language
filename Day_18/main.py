#!/usr/bin/env python3

import re
import sys
from collections import namedtuple
from copy import copy
from enum import Enum
import numpy as np

Instruction = namedtuple('Instruction', 'direction distance colour')

class Tile(Enum):
    NONE = '.'
    VERTICAL = '|'
    HORIZONTAL = '-'
    TOP_LEFT = 'F'
    TOP_RIGHT = '7'
    BOTTOM_LEFT = 'L'
    BOTTOM_RIGHT = 'J'

def prettify_tile(tile):
    match tile:
        case Tile.NONE:
            return "X"
        case Tile.VERTICAL:
            return "║"
        case Tile.HORIZONTAL:
            return "═"
        case Tile.TOP_LEFT:
            return "╔"
        case Tile.TOP_RIGHT:
            return "╗"
        case Tile.BOTTOM_LEFT:
            return "╚"
        case Tile.BOTTOM_RIGHT:
            return "╝"
        case _:
            raise Exception(f"Unknown tile {tile}")

def prettify_path(grid, path):
    pretty = np.full_like(grid, "░")
    for index in path:
        pretty[index] = prettify_tile(grid[index])
    return pretty

def parse_input(filename, fix_colours):
    instructions = []
    prog = re.compile("^([UDLR]{1}) ([0-9]+) \(#([0-9a-f]{6})\)$")
    with open(filename) as f:
        for line in f.readlines():
            line = line.strip()
            m = prog.match(line)
            instructions.append(Instruction(m.group(1), int(m.group(2)), m.group(3)))
    if not fix_colours:
        return instructions

    new_instructions = []
    for instruction in instructions:
        match instruction.colour[-1]:
            case "0":
                new_direction = "R"
            case "1":
                new_direction = "D"
            case "2":
                new_direction = "L"
            case "3":
                new_direction = "U"
            case direction:
                raise Exception(f"Unknown direction {direction}")
        new_distance = int(instruction.colour[0:5], 16)
        new_instructions.append(Instruction(new_direction, new_distance, instruction.colour))

    return new_instructions

def index_is_in_grid(index, grid):
    return index[0] >= 0 and index[0] < len(grid) and index[1] >= 0 and index[1] < len(grid[0])

def dig_path(instructions):
    current = (0, 0)
    path = [current]
    for instruction in instructions:
        if instruction.direction == 'U':
            for i in range(instruction.distance):
                path.append((current[0] - 1, current[1]))
                current = path[-1]
        elif instruction.direction == 'D':
            for i in range(instruction.distance):
                path.append((current[0] + 1, current[1]))
                current = path[-1]
        elif instruction.direction == 'L':
            for i in range(instruction.distance):
                path.append((current[0], current[1] - 1))
                current = path[-1]
        elif instruction.direction == 'R':
            for i in range(instruction.distance):
                path.append((current[0], current[1] + 1))
                current = path[-1]

    # Check we actually made a loop
    assert path[0] == path[-1]
    return path[0:-1]

def indices_to_the_right(current, next, next_type):
    """This function consider a movement from the current square to the next square. It then
    returns the index of the square to the "right" of the next square from the perspective of
    someone travelling in the direction current->next.

    We must also consider what type of square we're moving into. If it's a corner then we may
    also need to add the other square to the right of the corner after turning the corner.
    """
    ret = []
    if current[0] == next[0]:
        # We went left or right
        if current[1] < next[1]:
            # We went right
            ret.append((next[0] + 1, next[1]))
            if next_type == Tile.BOTTOM_RIGHT:
                ret.append((next[0], next[1] + 1))
            return ret
        else:
            # We went left
            ret.append((next[0] - 1, next[1]))
            if next_type == Tile.TOP_LEFT:
                ret.append((next[0], next[1] - 1))
            return ret
    elif current[1] == next[1]:
        # We went up or down
        if current[0] < next[0]:
            # We went down
            ret.append((next[0], next[1] - 1))
            if next_type == Tile.BOTTOM_LEFT:
                ret.append((next[0] + 1, next[1]))
            return ret
        else:
            # We went up
            ret.append((next[0], next[1] + 1))
            if next_type == Tile.TOP_RIGHT:
                ret.append((next[0] - 1, next[1]))
            return ret
    else:
        raise Exception(f"Can't find index to the right of {current} and {next}")

def horiz_or_vert_betwee_indices(before, after):
    if before[0] == after[0]:
        if before[1] < after[1]:
            return "R"
        else:
            return "L"
    elif before[1] == after[1]:
        if before[0] < after[0]:
            return "D"
        else:
            return "U"

def compute_next_tile_type(current, next, next_next):
    pipes = horiz_or_vert_betwee_indices(current, next) + horiz_or_vert_betwee_indices(next, next_next)

    # all_cases = ["RR", "RU", "RD", "LL", "LU", "LD", "UU", "UR", "UL", "DD", "DR", "DL"]
    match pipes:
        case "RR" | "LL":
            return Tile.HORIZONTAL
        case "UU" | "DD":
            return Tile.VERTICAL
        case "RU" | "DL":
            return Tile.BOTTOM_RIGHT
        case "RD" | "UL":
            return Tile.TOP_RIGHT
        case "LU" | "DR":
            return Tile.BOTTOM_LEFT
        case "LD" | "UR":
            return Tile.TOP_LEFT
        case _:
            raise Exception(f"Unknown pipe combination {pipes}")

def find_all_squares_to_the_immediate_right_of_the_loop(grid, loop):
    loop_copy = copy(loop)
    loop_copy.append(loop[0])

    right_hand_side_of_loop = []
    for i in range(0, len(loop_copy) - 1):
        indices = indices_to_the_right(loop_copy[i], loop_copy[i+1], grid[loop_copy[i+1]])
        for index in indices:
            if index in loop_copy:
                continue
            if not index_is_in_grid(index, grid):
                continue
            right_hand_side_of_loop.append(index)

    return right_hand_side_of_loop

def next_directions_from_grid_entry(tile, start):
    match tile:
        case Tile.VERTICAL:
            return [(start[0] + 1, start[1]), (start[0] - 1, start[1])]
        case Tile.HORIZONTAL:
            return [(start[0], start[1] + 1), (start[0], start[1] - 1)]
        case Tile.TOP_LEFT:
            return [(start[0], start[1] + 1), (start[0] + 1, start[1])]
        case Tile.TOP_RIGHT:
            return [(start[0], start[1] - 1), (start[0] + 1, start[1])]
        case Tile.BOTTOM_LEFT:
            return [(start[0], start[1] + 1), (start[0] - 1, start[1])]
        case Tile.BOTTOM_RIGHT:
            return [(start[0], start[1] - 1), (start[0] - 1, start[1])]
        case Tile.START | Tile.NONE:
            return []
        case _:
            raise Exception(f"Unknown tile {tile}")

def all_directions_from_grid_entry(index):
    return next_directions_from_grid_entry(Tile.HORIZONTAL, index) + next_directions_from_grid_entry(Tile.VERTICAL, index)

def flood(grid, loop, index):
    """A flood fill algorithim. We are effectively doing an A* style search, i.e. we radiate out
    from the start index, find new indices that can be flooded then radiate out from them. We
    ignore squares we've already filled. We stop when we find no new squares."""
    flooded_indices = set([index])
    next_indices_to_fill_from = [index]
    done = np.full_like(grid, False)
    for i in loop:
        done[i] = True

    while len(next_indices_to_fill_from) > 0:
        next_indices_to_fill_from_in_next_loop = []
        for next_index in next_indices_to_fill_from:
            for index in all_directions_from_grid_entry(next_index):
                if not index_is_in_grid(index, grid):
                    continue
                if done[index]:
                    continue
                flooded_indices.add(index)
                done[index] = True
                next_indices_to_fill_from_in_next_loop.append(index)
        next_indices_to_fill_from = next_indices_to_fill_from_in_next_loop
    return flooded_indices

def flood_fill(grid, loop, indices_to_flood):
    """Given a list of indices we "flood fill" from each of those indices then take the union
    off all squares which get filled from flooding from each of those."""
    flooded_indices = set()
    for index in set(indices_to_flood):
        if index in flooded_indices:
            continue
        flooded_indices = flooded_indices.union(flood(grid, loop, index))
    return flooded_indices

def grid_bounds_from_loop(loop):
    min_x = sys.maxsize
    max_x = -sys.maxsize
    min_y = sys.maxsize
    max_y = -sys.maxsize

    for index in loop:
        if index[0] < min_x:
            min_x = index[0]
        if index[0] > max_x:
            max_x = index[0]
        if index[1] < min_y:
            min_y = index[1]
        if index[1] > max_y:
            max_y = index[1]
    return (min_x, max_x, min_y, max_y)

def rebase_indices(path):
    min_x, _, min_y, _ = grid_bounds_from_loop(path)
    rebased = []
    for index in path:
        rebased.append((index[0] - min_x, index[1] - min_y))
    return rebased

def add_loop_to_grid(grid, loop):
    loop_copy = [loop[-1]] + copy(loop)
    loop_copy.append(loop[0])
    loop_copy.append(loop[1])

    for i in range(0, len(loop_copy) - 2):
        type = compute_next_tile_type(loop_copy[i], loop_copy[i+1], loop_copy[i+2])
        grid[loop_copy[i+1]] = type

def answer_part1(filename):
    instructions = parse_input(filename, fix_colours=False)
    loop = dig_path(instructions)
    loop = rebase_indices(loop)

    min_x, max_x, min_y, max_y = grid_bounds_from_loop(loop)
    assert min_x == 0
    assert min_y == 0
    grid = np.full((max_x + 1, max_y + 1), fill_value=Tile.NONE, dtype=object)
    add_loop_to_grid(grid, loop)
    pretty = prettify_path(grid, loop)
    for i in range(0, len(pretty)):
        print("".join(pretty[i]))

    print("="*20)
    indices = find_all_squares_to_the_immediate_right_of_the_loop(grid, loop)
    print(indices)
    pretty = prettify_path(grid, indices)
    for i in range(0, len(pretty)):
        print("".join(pretty[i]))

    print("="*20)
    flooded_incides = flood_fill(grid, loop, indices)
    pretty = prettify_path(grid, flooded_incides)
    for i in range(0, len(pretty)):
        print("".join(pretty[i]))

    ret = len(loop) + len(flooded_incides)
    print(ret)
    return ret

assert len(dig_path(parse_input("test_input.txt", fix_colours=False))) == 38
assert answer_part1("test_input.txt") == 62
assert answer_part1("real_input.txt") == 48652
# assert answer_part1("test_input.txt", fix_colours=True) == 952408144115
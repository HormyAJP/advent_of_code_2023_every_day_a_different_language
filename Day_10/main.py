#!/usr/bin/env python3

from copy import copy
from enum import Enum
import numpy as np

class Tile(Enum):
    NONE = '.'
    VERTICAL = '|'
    HORIZONTAL = '-'
    TOP_LEFT = 'F'
    TOP_RIGHT = '7'
    BOTTOM_LEFT = 'L'
    BOTTOM_RIGHT = 'J'
    START = 'S'

def prettify_tile(tile):
    match tile:
        case Tile.NONE:
            return " "
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
        case Tile.START:
            return "S"
        case _:
            raise Exception(f"Unknown tile {tile}")

def parse_input(filename):
    with open(filename) as f:
        data = [line.strip() for line in f.readlines()]
    ret = np.empty((len(data), len(data[0])), dtype=Tile)
    for i, line in enumerate(data):
        for j, char in enumerate(line):
            ret[i][j] = Tile(char)
    return ret

def prettify_path(grid, path):
    pretty = np.full_like(grid, "░")
    for index in path:
        pretty[index] = prettify_tile(grid[index])
    return pretty

def prettify_filled_indices(pretty_grid, indices):
    for index in indices:
        pretty_grid[index] = 'R'

def pretty_print(pretty_grid):
    for row in pretty_grid:
        print("".join(row))

def start_position(grid):
    for i, row in enumerate(grid):
        for j, tile in enumerate(row):
            if tile == Tile.START:
                return i, j
    raise Exception("No start position found")

def all_directions_from_grid_entry(index):
    return next_directions_from_grid_entry(Tile.HORIZONTAL, index) + next_directions_from_grid_entry(Tile.VERTICAL, index)

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

def index_is_in_grid(index, grid):
    return index[0] >= 0 and index[0] < len(grid) and index[1] >= 0 and index[1] < len(grid[0])

def path_is_a_loop(grid, loop_entries, current):
    previous = loop_entries[0]
    while current != loop_entries[0]:
        type_ = grid[current]
        next = next_directions_from_grid_entry(type_, current)
        if len(next) == 0:
            # print(f"Not a loop because {current} ({type_}) isn't a pipe")
            return False
        if previous not in next:
            # print(f"Not a loop because {current} ({type_}) doesn't connect back to the previous entry {previous}")
            return False
        next.remove(previous)
        loop_entries.append(current)
        # print(f"Moving from {current} -> {next[0]}")
        previous = current
        current = next[0]

    return True

def compute_start_loop(grid):
    start = start_position(grid)
    # print(f"Start position is ({start})")

    next_locations = [
        (start[0] + 1, start[1]),
        (start[0], start[1] + 1),
        (start[0] - 1, start[1]),
        (start[0], start[1] - 1)]

    for next_location in next_locations:
        if next_location[0] < 0 or next_location[0] >= len(grid):
            continue
        if next_location[1] < 0 or next_location[1] >= len(grid[0]):
            continue
        loop_entries = [start]
        # print(f"Starting at {start} and moving to {next_location}")
        if path_is_a_loop(grid, loop_entries, next_location):
            return loop_entries
    raise Exception("No loop found")

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

# Test cases for indices_to_the_right
all_test_tiles_of_interest = [Tile.VERTICAL, Tile.HORIZONTAL, Tile.TOP_LEFT, Tile.TOP_RIGHT, Tile.BOTTOM_LEFT, Tile.BOTTOM_RIGHT]
# Test moving right
test_tiles = copy(all_test_tiles_of_interest)
test_tiles.remove(Tile.BOTTOM_RIGHT)
for test_tile in test_tiles:
    assert indices_to_the_right((10, 10), (10, 11), test_tile) == [(11, 11)]
assert indices_to_the_right((10, 10), (10, 11), Tile.BOTTOM_RIGHT) == [(11, 11), (10, 12)]
# Test moving left
test_tiles = copy(all_test_tiles_of_interest)
test_tiles.remove(Tile.TOP_LEFT)
for test_tile in test_tiles:
    assert indices_to_the_right((10, 10), (10, 9), test_tile) == [(9, 9)]
assert indices_to_the_right((10, 10), (10, 9), Tile.TOP_LEFT) == [(9, 9), (10, 8)]
# Test moving Down
test_tiles = copy(all_test_tiles_of_interest)
test_tiles.remove(Tile.BOTTOM_LEFT)
for test_tile in test_tiles:
    assert indices_to_the_right((10, 10), (11, 10), test_tile) == [(11, 9)]
assert indices_to_the_right((10, 10), (11, 10), Tile.BOTTOM_LEFT) == [(11, 9), (12, 10)]
# Test moving Up
test_tiles = copy(all_test_tiles_of_interest)
test_tiles.remove(Tile.TOP_RIGHT)
for test_tile in test_tiles:
    assert indices_to_the_right((10, 10), (9, 10), test_tile) == [(9, 11)]
assert indices_to_the_right((10, 10), (9, 10), Tile.TOP_RIGHT) == [(9, 11), (8, 10)]

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

def flood(grid, loop, index):
    """A flood fill algorithim. We are effectively doing an A* style search, i.e. we radiate out
    from the start index, find new indices that can be flooded then radiate out from them. We
    ignore squares we've already filled. We stop when we find no new squares."""
    flooded_indices = [index]
    next_indices_to_fill_from = [index]
    while len(next_indices_to_fill_from) > 0:
        next_indices_to_fill_from_in_next_loop = []
        for next_index in next_indices_to_fill_from:
            for index in all_directions_from_grid_entry(next_index):
                if index in flooded_indices:
                    continue
                if not index_is_in_grid(index, grid):
                    continue
                if index in loop:
                    continue
                flooded_indices.append(index)
                next_indices_to_fill_from_in_next_loop.append(index)
        next_indices_to_fill_from = next_indices_to_fill_from_in_next_loop
    return flooded_indices

def flood_fill(grid, loop, indices_to_flood):
    """Given a list of indices we "flood fill" from each of those indices then take the union
    off all squares which get filled from flooding from each of those."""
    flooded_indices = []
    for index in set(indices_to_flood):
        if index in flooded_indices:
            continue
        flooded_indices += flood(grid, loop, index)
    return flooded_indices

def answer_part_1(filename):
    grid = parse_input(filename)
    loop = compute_start_loop(grid)
    return len(loop) // 2

def answer_part_2(filename):
    """I was lazy with part 2. There's a final step needed but since that just helps choose one
    answer from a possible 2 I decided to just guess which to use. AoC allows me to retry after 1
    minute.

    Here's what this code actually does.

    1) First find the loop as per part 1.
    2) Next, follow the loop around. The direction is arbitrary. We don't actually know which is
       the "correct" direction and it doesn't matter.
    3) As we follow the loop around we make a note of every square to the right of the loop which
       isn't on the loop or out of bounds.
    4) Once we have this list of squares to the right, we basically do a flood fill, starting at
       each of those squares. This will fill out either the entire INTERIOR of the loop or the
       entire EXTERIOR of the loop. We don't know which because we don't know which way the loop
       is "oriented". I'm effectively picking an arbitrary orientation by looking to the right of
       the loop. This doesn't really matter because now we can count the interior and the exterior
       number of squares. Our answer must be one of those two values.

       N.B. I could have solved this properly by searching from the outside of the grid inwards for
       any square that wasn't ON the loop. Once I have one, I just check if it's in the squares
       from the flood fill. If it is, then we computed the exterior, otherwise we computed the
       interior.
    """
    grid = parse_input(filename)
    loop = compute_start_loop(grid)
    pretty = prettify_path(grid, loop)
    print()
    pretty_print(pretty)
    print()
    flood_start_indicies = find_all_squares_to_the_immediate_right_of_the_loop(grid, loop)
    prettify_filled_indices(pretty, flood_start_indicies)
    pretty_print(pretty)
    print()
    flooded_incides = flood_fill(grid, loop, flood_start_indicies)
    return len(flooded_incides), grid.size - len(flooded_incides) - len(loop)

assert answer_part_1("./test_input1.txt") == 4
assert answer_part_1("./test_input2.txt") == 8
assert 4 in answer_part_2("./test_input3.txt")
assert 8 in answer_part_2("./test_input4.txt")
assert 10 in answer_part_2("./test_input5.txt")
print(f"Answer to part 2 is one of {answer_part_2('./real_input.txt')}")
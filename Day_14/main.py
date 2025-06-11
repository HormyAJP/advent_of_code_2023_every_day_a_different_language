#!/usr/bin/env python3

import numpy as np
from enum import Enum

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

def dump_grid(grid):
    for row in grid:
        print("".join(row))

def parse_input(filename):
    with open(filename) as f:
        lines = [list(line.strip()) for line in f.readlines()]
    return np.array(lines)

def tilt_grid_right_until_nothing_moves(grid):
    grid = np.rot90(grid, k=1)
    tilt_grid_up_until_nothing_moves(grid)
    grid = np.rot90(grid, k=3)

def tilt_grid_left_until_nothing_moves(grid):
    grid = np.rot90(grid, k=3)
    tilt_grid_up_until_nothing_moves(grid)
    grid = np.rot90(grid, k=1)

def tilt_grid_down_until_nothing_moves(grid):
    grid = np.rot90(grid, k=2)
    tilt_grid_up_until_nothing_moves(grid)
    grid = np.rot90(grid, k=2)

def tilt_grid_up_until_nothing_moves(grid):
    something_moved = True
    while something_moved:
        something_moved = False
        for irow in range(1, len(grid)):
            for icol in range(len(grid[irow])):
                if grid[irow, icol] in ['#', '.']:
                    continue
                if grid[irow - 1, icol] == ".":
                    grid[irow - 1, icol] = "O"
                    grid[irow, icol] = "."
                    something_moved = True

def perform_one_spin_cycle(grid):
    tilt_grid_up_until_nothing_moves(grid)
    tilt_grid_left_until_nothing_moves(grid)
    tilt_grid_down_until_nothing_moves(grid)
    tilt_grid_right_until_nothing_moves(grid)

def calculate_load(grid):
    num_rows = len(grid)
    load = 0
    for irow in range(num_rows):
        for icol in range(len(grid[irow])):
            if grid[irow, icol] == "O":
                load += num_rows - irow
    return load

def answer_part1(filename):
    grid = parse_input(filename)
    tilt_grid_up_until_nothing_moves(grid)
    return calculate_load(grid)

def hash_grid(grid):
    return "".join(["".join(row) for row in grid])

def answer_part2(filename):
    NUM_CYCLES = 1000000000
    grid = parse_input(filename)
    print()
    hashes = {}
    istep = 0
    end_of_first_cycle = None
    while 1:
        hsh = hash_grid(grid)
        if hsh in hashes:
            if end_of_first_cycle is None:
                print(f"Found first loop at step {istep}")
                end_of_first_cycle = istep
                istep = 0
                hashes = {hsh: 0}
            else:
                break
        else:
            hashes[hsh] = istep
        perform_one_spin_cycle(grid)
        istep += 1

    print(f"Cycle found {istep}")
    remainder = (NUM_CYCLES - end_of_first_cycle) % istep
    for i in range(remainder):
        perform_one_spin_cycle(grid)
    return calculate_load(grid)

assert answer_part1("test_input.txt") == 136
assert answer_part1("real_input.txt") == 109638
assert answer_part2("test_input.txt") == 64
print(answer_part2("real_input.txt"))
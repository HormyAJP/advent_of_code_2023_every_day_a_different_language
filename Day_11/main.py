#!/usr/bin/env python3

import numpy as np
from functools import partial

def parse_input(filename):
    with open(filename) as f:
        lines = [list(line.strip()) for line in f.readlines()]
    return np.array(lines)

def expand_universe(universe):
    new_rows = []
    for irow, row in enumerate(universe):
        new_rows.append(row)
        if set(row) == set(["."]):
            new_rows.append(row)

    universe = np.array(new_rows)

    new_cols = []
    for icol, col in enumerate(universe.T):
        new_cols.append(col)
        if set(col) == set(["."]):
            new_cols.append(col)

    return np.array(new_cols).T

def distance_between_galaxies(index1, index2):
    return abs(index2[1] - index1[1]) + abs(index2[0] - index1[0])

def coorindates_of_galaxies(universe):
    coords = []
    for irow, row in enumerate(universe):
        for icol, col in enumerate(row):
            if col == "#":
                coords.append((irow, icol))
    return coords

def answer_part1(filename):
    universe = parse_input(filename)
    universe = expand_universe(universe)
    coords = coorindates_of_galaxies(universe)
    sum_distances = 0
    for icoord, coord in enumerate(coords):
        for j in range(icoord + 1, len(coords)):
            sum_distances += distance_between_galaxies(coord, coords[j])
    return sum_distances


expanded_test = """\
....#........
.........#...
#............
.............
.............
........#....
.#...........
............#
.............
.............
.........#...
#....#......."""

# assert (np.array([list(row) for row in expanded_test.split()]) == expand_universe(parse_input("test_input.txt"))).all()
# assert answer_part1("test_input.txt") == 374
# assert answer_part1("real_input.txt") == 9556896

def expansion_rows_and_columns(universe):
    rows = []
    cols = []
    for irow, row in enumerate(universe):
        if set(row) == set(["."]):
            rows.append(irow)
    for icol, col in enumerate(universe.T):
        if set(col) == set(["."]):
            cols.append(icol)
    return rows, cols

def distance_between_galaxies_with_expansion_info(index1, index2, exanded_rows_and_cols, expansion_factor=1_000_000):
    """It is assumed that exanded_rows_and_cols will be sorted"""
    def filter_function(lower_index, upper_index, index):
        return lower_index <= index <= upper_index or upper_index <= index <= lower_index

    bound_filter = partial(filter_function, index1[0], index2[0])
    filtered_rows = list(filter(bound_filter, exanded_rows_and_cols[0]))
    # print(filtered_rows)
    num_expanded_rows = len(filtered_rows)

    bound_filter = partial(filter_function, index1[1], index2[1])
    filtered_cols = list(filter(bound_filter, exanded_rows_and_cols[1]))
    # print(filtered_cols)
    num_expanded_cols = len(filtered_cols)

    ret = distance_between_galaxies(index1, index2) + (num_expanded_rows + num_expanded_cols) * (expansion_factor - 1)
    # print(f"Distance between {index1} and {index2} is {ret}")
    return ret

assert distance_between_galaxies_with_expansion_info((0, 0), (0, 2), ([], [1]), expansion_factor=1) == 2
assert distance_between_galaxies_with_expansion_info((0, 0), (0, 2), ([], [1]), expansion_factor=10) == 11
assert distance_between_galaxies_with_expansion_info((0, 0), (0, 2), ([], [1]), expansion_factor=100) == 101

assert distance_between_galaxies_with_expansion_info((0, 0), (2, 0), ([1], []), expansion_factor=1) == 2
assert distance_between_galaxies_with_expansion_info((0, 0), (2, 0), ([1], []), expansion_factor=10) == 11
assert distance_between_galaxies_with_expansion_info((0, 0), (2, 0), ([1], []), expansion_factor=100) == 101

assert distance_between_galaxies_with_expansion_info((0, 0), (2, 2), ([1], [1]), expansion_factor=1) == 4
assert distance_between_galaxies_with_expansion_info((0, 0), (2, 2), ([1], [1]), expansion_factor=10) == 22

assert distance_between_galaxies_with_expansion_info((0, 0), (2, 2), ([], [1]), expansion_factor=1) == 4
assert distance_between_galaxies_with_expansion_info((0, 0), (2, 2), ([], [1]), expansion_factor=10) == 13

assert distance_between_galaxies_with_expansion_info((0, 0), (2, 2), ([3], [3]), expansion_factor=100) == 4
assert distance_between_galaxies_with_expansion_info((3, 4), (10, 17), ([5, 9, 10], [11, 12, 13, 17]), expansion_factor=100) == 4 + 9 + 100 * 7

assert distance_between_galaxies_with_expansion_info((0, 3), (1, 7), ([], [2,5,8]), expansion_factor=10) == 14

def answer_part2(filename, expansion_factor):
    universe = parse_input(filename)
    coords = coorindates_of_galaxies(universe)
    exanded_rows_and_cols = expansion_rows_and_columns(universe)
    sum_distances = 0
    for icoord, coord in enumerate(coords):
        for j in range(icoord + 1, len(coords)):
            sum_distances += distance_between_galaxies_with_expansion_info(coord, coords[j], exanded_rows_and_cols, expansion_factor=expansion_factor)
    # print(f"Sum distances: {sum_distances}")
    return sum_distances

assert answer_part2("test_input.txt", expansion_factor=10) == 1030
assert answer_part2("test_input.txt", expansion_factor=100) == 8410
print(answer_part2("real_input.txt", expansion_factor=1_000_000) )
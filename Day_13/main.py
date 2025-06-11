#!/usr/bin/env python

import numpy as np

def parse_input(filename):
    with open(filename) as f:
        lines = [line.strip() for line in f.readlines()]
        lines.append("") # Make logic below easier

    patterns = []
    rows_in_this_pattern = []
    for line in lines:
        if len(line) == 0:
            patterns.append(np.array(rows_in_this_pattern))
            rows_in_this_pattern = []
        else:
            rows_in_this_pattern.append(list(line))
    return patterns

def find_reflection_line(pattern):
    for i in range(1, len(pattern[0])):
        match = i
        # The reflection line will be to the left of i
        max_to_check = min(i, len(pattern[0]) - i)
        for j in range(0, max_to_check):
            if (pattern.T[i - 1 - j] != pattern.T[i + j]).any():
                match = None
                break
        if match is not None:
            return match
    return None

def row_or_column_is_the_same_assuming_smudge(arr1, arr2):
    comparison = (arr1 != arr2)
    ret = np.count_nonzero(comparison) in [0, 2]
    print(f"Comparing {arr1} and {arr2}: they are {'' if ret else 'NOT '}the same")
    return ret

def find_reflection_line_assuming_smudge(pattern, ignore_me):
    for i in range(1, len(pattern[0])):
        if i == ignore_me:
            continue
        match = i
        smudge_count = 0
        # The reflection line will be to the left of i
        max_to_check = min(i, len(pattern[0]) - i)
        for j in range(0, max_to_check):
            diff_count = np.count_nonzero(pattern.T[i - 1 - j] !=  pattern.T[i + j])
            if diff_count > 1:
                match = None
                break
            elif diff_count == 1:
                if smudge_count > 0:
                    match = None
                    break
                else:
                    smudge_count += 1
        if match is not None:
            return match
    return None

def find_reflection_line_for_pattern(pattern):
    match = find_reflection_line(pattern)
    if match is not None:
        return ("COL", match)
    match = find_reflection_line(pattern.T)
    if match is not None:
        return ("ROW", match)
    raise Exception(f"Couldn't fine reflection for pattern {pattern}")

def find_reflection_line_for_pattern_assuming_smudge(pattern):
    ignore_me = find_reflection_line(pattern)
    if ignore_me is not None:
        print(f"Looking for reflection column")
        match = find_reflection_line_assuming_smudge(pattern, ignore_me)
        print(f"Found reflection column {match} for pattern\n {pattern}\n whilst ignoring {ignore_me}")
        if match is not None:
            return ("COL", match)
    else:
        print(f"Looking for reflection row")
        match = find_reflection_line_assuming_smudge(pattern, -1)
        print(f"Found reflection column {match} for pattern\n {pattern}")
        if match is not None:
            return ("COL", match)

    ignore_me = find_reflection_line(pattern.T)
    if ignore_me is not None:
        match = find_reflection_line_assuming_smudge(pattern.T, ignore_me)
        print(f"Found reflection row {match} for pattern\n {pattern}\n whilst ignoring {ignore_me}")
        if match is not None:
            return ("ROW", match)
    else:
        match = find_reflection_line_assuming_smudge(pattern.T, -1)
        print(f"Found reflection row {match} for pattern\n {pattern}")
        if match is not None:
            return ("ROW", match)
    raise Exception(f"Couldn't fine reflection for pattern {pattern}")

def answer_part1(filename):
    patterns = parse_input(filename)
    total = 0
    for pattern in patterns:
        ref = find_reflection_line_for_pattern(pattern)
        if ref[0] == "COL":
            total += ref[1]
        else:
            total += ref[1] * 100
    return total

def answer_part2(filename):
    patterns = parse_input(filename)
    total = 0
    for pattern in patterns:
        ref = find_reflection_line_for_pattern_assuming_smudge(pattern)
        if ref[0] == "COL":
            total += ref[1]
        else:
            total += ref[1] * 100
    return total


print(answer_part1("real_input.txt"))
print(answer_part2("test_input.txt"))
print(answer_part2("real_input.txt"))

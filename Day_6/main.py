#!/usr/bin/env python3

import math

def answer_for_input_file(filename, smoosh_numbers=False):
    with open(filename) as f:
        data = f.readlines()

    # Don't do this in prod 😂
    if smoosh_numbers:
        times = [int("".join(data[0].replace("Time:", "").split()))]
        distances = [int("".join(data[1].replace("Distance:", "").split()))]
    else:
        times = [int(time) for time in data[0].replace("Time:", "").split()]
        distances = [int(time) for time in data[1].replace("Distance:", "").split()]
    time_and_distance_pairs = zip(times, distances)

    result = 1
    for time_and_distance_pair in time_and_distance_pairs:
        ret = num_ways_of_winning_race(*time_and_distance_pair)
        print(f"There are {ret} ways of winning race {time_and_distance_pair}")
        result *= ret
    return result

def num_ways_of_winning_race(time, distance):
    # If this isn't true then the record isn't beatable
    assert (time > 2 * math.sqrt(distance))

    lower_bound = (time - math.sqrt(time ** 2 - 4 * distance)) / 2
    if math.ceil(lower_bound) == lower_bound:
        lower_bound = int(lower_bound) + 1
    else:
        lower_bound = math.ceil(lower_bound)

    upper_bound = (time + math.sqrt(time ** 2 - 4 * distance)) / 2
    if math.floor(upper_bound) == upper_bound:
        upper_bound = int(upper_bound) - 1
    else:
        upper_bound = math.floor(upper_bound)

    # Sanity check that our bounds are optimal
    assert (time - upper_bound) * upper_bound > distance
    assert (time - (upper_bound+1)) * (upper_bound+1) <= distance
    assert (time - lower_bound) * lower_bound > distance
    assert (time - (lower_bound-1)) * (lower_bound-1) <= distance

    return upper_bound - lower_bound + 1

assert answer_for_input_file("test_input.txt") == 288
assert answer_for_input_file("real_input.txt") == 633080
assert answer_for_input_file("test_input.txt", smoosh_numbers=True) == 71503
print(answer_for_input_file("real_input.txt", smoosh_numbers=True))

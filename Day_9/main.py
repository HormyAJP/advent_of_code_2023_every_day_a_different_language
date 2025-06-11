#!/usr/bin/env python3

import math

def parse_input(filename):
    sequences = []
    with open(filename) as f:
        string_sequences = [line.split() for line in f.readlines()]
    for sequence in string_sequences:
        sequences.append([int(element) for element in sequence])
    return sequences

def num_diffs_to_stabilise(sequence):
    input_sequence = sequence
    diffs = 0
    while set(sequence) != set([0]):
        sequence = [ x - y for (x, y) in zip(sequence[1:], sequence[:-1])]
        diffs += 1
    print(f"{diffs} iterations to stabilise {input_sequence}")
    return diffs

def next_value_in_sequence(sequence):
    """In order to compute the next value in a sequence we use the following formula (which of
    course needs to be proved 😁)

    Given a sequence {a_n} which "stabilizes" after n steps, the next value in the sequence is given
    by:

    a_(k+1) = (n choose 1) * a_k - (n choose 2) * a_(k-1) + (n choose 3) * a_(k-2) - ...
                    + (-1)^n * (n choose n) * a_(k-n)

    By "stablize" we mean the number of steps before the differences of a sequence become zero.

    e.g. If a sequence stabilises after 1 step then a_(k+1) = 2 * a_k - a_(k-1)
    e.g. If a sequence stabilises after 2 steps then a_(k+1) = 3 * a_k - 3 * a_(k-1) + a_(k-2)

    """
    n = num_diffs_to_stabilise(sequence)
    coefficients = [0] * len(sequence)
    start_sign = 1
    for i in range(1, n+1):
        coefficients[i-1] = math.comb(n, i) * start_sign
        start_sign *= -1
    # print(f"Coefficients are {coefficients}")

    next_value = sum([x * y for (x, y) in zip(reversed(sequence), coefficients)])
    return next_value

def answer_part_1(filename):
    total = 0
    for sequence in parse_input(filename):
        total += next_value_in_sequence(sequence)
    return total

assert answer_part_1('test_input.txt')  == 114
assert answer_part_1('real_input.txt')  == 1974232246

def answer_part_2(filename):
    total = 0
    sequences = parse_input(filename)
    sequences = [list(reversed(sequence)) for sequence in sequences]
    for sequence in sequences:
        total += next_value_in_sequence(sequence)
    return total

assert answer_part_2('test_input.txt')  == 2
print(f"Answer to part 2 is {answer_part_2('real_input.txt')}")
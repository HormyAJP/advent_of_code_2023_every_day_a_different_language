#!/usr/bin/env python3

import time

# Cheap debugging. Not worth important logging
DEBUGGING = 1
def debug(msg):
    if DEBUGGING:
        print(msg)

def parse_input(filename):
    ret = []
    with open(filename) as f:
        for line in f.readlines():
            conditions, counts = line.split()
            counts = [int(num) for num in counts.split(",")]
            ret.append((conditions, counts))
    return ret

def unfold_inputs_for_part2(conditions_and_counts):
    return [("?".join([conditions] * 5), counts * 5) for conditions, counts in conditions_and_counts]

def recurse(contiguous_blocks, counts):
    debug(f"recurse: Recursing with contiguous blocks {contiguous_blocks} and counts {counts}")
    # If we've no more counts left to allocate then we're almost done. However, we must check
    # that none of the remaining blocks have a "#" in them, otherwise we have a known bad spring
    # which isn't accounted for
    if len(counts) == 0:
        debug(f"recurse: No more counts")
        for remaining_block in contiguous_blocks:
            if "#" in remaining_block:
                debug(f"recurse: Bad arrangement. We still have this block remaining {remaining_block}")
                return 0
        # This is the only branch of this function which can return 1. It's basically a terminal
        # branch. We've found an arrangement that works.
        debug("recurse: Found good arrangement")
        return 1

    front_count = counts[0]
    total_possilities = 0
    while 1:
        # We next have to find the next block that works with the next count.
        front_block_index = None
        debug(f"Looking for a block for count {front_count} of bad springs")
        for i in range(0, len(contiguous_blocks)):
            # This block works because it's big enough to hold the next count.
            if len(contiguous_blocks[i]) >= front_count:
                front_block_index = i
                debug(f"recurse: We can use the block {contiguous_blocks[i]} to hold the next count")
                break
            # If we get here it means the block is too small to hold the next count. That's okay
            # if the block just contains "?"s, but it it contains a known bad spring then this
            # arrangement is invalid.
            if "#" in contiguous_blocks[i]:
                debug(f"recurse: Bad arrangement. We have a block {contiguous_blocks[i]} that's too small but contains a bad spring")
                return total_possilities

        # We couldn't find a block big enough to hold our count, so we have a bad arrangement.
        if front_block_index is None:
            debug(f"recurse: Bad arrangement. Couldn't find a block big enough to hold the next count")
            return total_possilities

        # Throw away blocks we've skipped (if any)
        contiguous_blocks = contiguous_blocks[front_block_index:]
        front_block = contiguous_blocks[0]

        maxi = len(front_block) - front_count + 1
        # Basically slide along the block we have available and try to fit out count in.
        debug(f"recurse: We have {maxi} possible starting positions in {front_block} for our count {front_count}")
        for i in range(0, maxi):
            debug(f"Trying position {i}/{maxi - 1} for {front_count} sprints in {front_block}")
            if i != 0 and front_block[i - 1] == "#":
                debug(f"recurse: Can't try any more positions because the previous character is a bad spring which would then be unallocated")
                break
            if i == maxi - 1:
                # We at the end of the front block so there won't be anything left to handover. We
                # don't need to worry about ensuring the next character is a good spring (or we're
                # at the end of the row). That's already handled in the way we broke up the blocks.
                leftover = ""
            else:
                leftover = front_block[i + front_count:]
                if leftover[0] not in [".", "?"]:
                    debug(f"recurse: Can't start at position {i} because the next character cannot be a good spring")
                    continue
                leftover = leftover[1:]
            if len(leftover) == 0:
                total_possilities += recurse(contiguous_blocks[1:], counts[1:])
            else:
                total_possilities += recurse([leftover] + contiguous_blocks[1:], counts[1:])

        if "#" in front_block:
            debug(f"recurse: Our block {front_block} contains a bad spring so we can't ignore it and look further ahead for more blocks.")
            break
        contiguous_blocks = contiguous_blocks[1:]
    return total_possilities


def count_possibilities_for_row(conditions, counts):
    # Add a "." to the end of the conditions to make the logic below cleaner.
    conditions += "."

    contiguous_blocks = []
    current_block = ""
    for i in range(len(conditions)):
        if conditions[i] in ["#", "?"]:
            current_block += conditions[i]
        else:
            if len(current_block) == 0:
                continue
            contiguous_blocks.append(current_block)
            current_block = ""

    debug(f"Starting recursive call with contiguous blocks {contiguous_blocks} and counts {counts}")
    ret = recurse(contiguous_blocks, counts)
    print(f"{ret} possibilities for row {conditions} and counts {counts}")
    return ret

def validate1(conditions, counts):
    counts = list(reversed(counts))
    cur_length = 0
    conditions += "."
    for char in conditions:
        if char == "#":
            cur_length += 1
        else:
            if cur_length == 0:
                continue
            if len(counts) == 0:
                return False
            if cur_length != counts.pop():
                return False
            cur_length = 0
    if len(counts) != 0:
        return False
    return True

def brute1(conditions, counts):
    import itertools
    num_unknowns = conditions.count("?")
    permutations = list(itertools.product(["#", "."], repeat=num_unknowns))
    total = 0
    for permutation in permutations:
        permutation = list(permutation)
        new_conditions = ""
        for char in conditions:
            if char == "?":
                new_conditions += str(permutation.pop())
            else:
                new_conditions += char
        if validate1(new_conditions, counts):
            total += 1
    return total

# def brute_force(filename):
#     all_conditions_and_counts = parse_input(filename)
#     sum_of_all_arrangements = 0
#     for conditions_and_counts in all_conditions_and_counts:
#         sum_of_all_arrangements += brute1(conditions_and_counts[0], conditions_and_counts[1])
#     return sum_of_all_arrangements

def answer_part1(filename, brute_force_it=False):
    all_conditions_and_counts = parse_input(filename)
    sum_of_all_arrangements = 0
    count_function = brute1 if brute_force_it else count_possibilities_for_row
    for conditions_and_counts in all_conditions_and_counts:
        sum_of_all_arrangements += count_function(conditions_and_counts[0], conditions_and_counts[1])
    return sum_of_all_arrangements

# assert count_possibilities_for_row("???.###", [1,1,3]) == 1
# assert count_possibilities_for_row(".??..??...?##.", [1,1,3]) == 4
# assert count_possibilities_for_row("?#?#?#?#?#?#?#?", [1,3,1,6]) == 1
# assert count_possibilities_for_row("????.#...#...", [4,1,1]) == 1
# assert count_possibilities_for_row("######..#####.", [6,5]) == 1
# assert count_possibilities_for_row("????.######..#####.", [1,6,5]) == 4
# assert count_possibilities_for_row("?###????????", [3,2,1]) == 10
# assert count_possibilities_for_row("?#???..?.#?.", [2, 2, 1]) == 1
# assert count_possibilities_for_row("??????????.?????????.", [1, 6, 1, 3, 2]) == 34
# assert count_possibilities_for_row("??????????.", [4,1,1]) == 10
# assert count_possibilities_for_row(".????##.?.????.???", [2,2]) == 7
# assert count_possibilities_for_row(".?.????.???", [2]) == 5
# assert brute1("???.###", [1,1,3]) == 1
# assert brute1(".??..??...?##.", [1,1,3]) == 4
# assert brute1("?#?#?#?#?#?#?#?", [1,3,1,6]) == 1
# assert brute1("????.#...#...", [4,1,1]) == 1
# assert brute1("######..#####.", [6,5]) == 1
# assert brute1("????.######..#####.", [1,6,5]) == 4
# assert brute1("?###????????", [3,2,1]) == 10
# assert brute1("?#???..?.#?.", [2, 2, 1]) == 1
# assert brute1("??????????.?????????.", [1, 6, 1, 3, 2]) == 34
# assert brute1(".?.????.???", [2]) == 5
# assert answer_part1("test_input.txt") == 21

# t = time.process_time()
# assert answer_part1("real_input.txt", brute_force_it=False) == 7191
# elapsed_time = time.process_time() - t
# print(f"Time to get answer to part 1 WITHOUT brute force is {elapsed_time}")
# t = time.process_time()
# assert answer_part1("real_input.txt", brute_force_it=False) == 7191
# elapsed_time = time.process_time() - t
# print(f"Time to get answer to part 1 WITH brute force is {elapsed_time}")

# def test(filename):
#     all_conditions_and_counts = parse_input(filename)
#     sum_of_all_arrangements = 0
#     for conditions_and_counts in all_conditions_and_counts:
#         val1 = count_possibilities_for_row(conditions_and_counts[0], conditions_and_counts[1])
#         val2 = brute1(conditions_and_counts[0], conditions_and_counts[1])
#         if val1 != val2:
#             print(f"ERROR: {conditions_and_counts[0]} {conditions_and_counts[1]}")
#             print(f"Logic: {val1}, Brute {val2}")
#             sys.exit(1)
#     return sum_of_all_arrangements

# test("real_input.txt")

def answer_part2(filename, brute_force_it=False):
    all_conditions_and_counts = parse_input(filename)
    all_conditions_and_counts = unfold_inputs_for_part2(all_conditions_and_counts)
    sum_of_all_arrangements = 0
    count_function = brute1 if brute_force_it else count_possibilities_for_row
    for conditions_and_counts in all_conditions_and_counts:
        sum_of_all_arrangements += count_function(conditions_and_counts[0], conditions_and_counts[1])
    return sum_of_all_arrangements

# assert answer_part2("test_input.txt") == 525152

t = time.process_time()
elapsed_time = time.process_time() - t
print(f"Answer to part 2 is {answer_part2('real_input.txt')}")
print(f"Time to get answer to part 2 WITHOUT brute force is {elapsed_time}")

# t = time.process_time()
# elapsed_time = time.process_time() - t
# print(f"Answer to part 2 is {answer_part2('test_input.txt', brute_force_it=True)}")
# print(f"Time to get answer to part 2 WITH brute force is {elapsed_time}")
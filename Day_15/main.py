#!/usr/bin/env python3

def hash_string(s):
    val = 0
    for c in s:
        val = ((val + ord(c))) * 17 % 256
    return val

assert hash_string("HASH") == 52
assert hash_string("rn=1") == 30

def parse_input(filename):
    with open(filename) as f:
        return f.readlines()[0].strip().split(",")

def answer_part1(filename):
    return sum([hash_string(step) for step in parse_input(filename)])

class HASHMAP:

    def __init__(self, size=256, hash_function=hash_string):
        self.size = size
        self.hash_function = hash_function
        self.hash_map = []
        for i in range(self.size):
            self.hash_map.append([[], []])

    def __setitem__(self, key, value):
        hash_value = self.hash_function(key)
        keys, values =  self.hash_map[hash_value]
        try:
            index = keys.index(key)
            values[index] = value
        except ValueError:
            keys.append(key)
            values.append(value)

    def __delitem__(self, key):
        hash_value = self.hash_function(key)
        keys, values =  self.hash_map[hash_value]
        try:
            index = keys.index(key)
            del keys[index]
            del values[index]
        except:
            pass

    def focussing_powers(self):
        total = 0
        for ibox, box in enumerate(self.hash_map):
            for ival, val in enumerate(box[1]):
                total += (1 + ibox) * (1 + ival) * val
        return total

def answer_part2(filename):
    steps = parse_input(filename)
    hmap = HASHMAP()
    for instruction in steps:
        # print(f"Executing instruction {instruction}")
        if "-" in instruction:
            key, _ = instruction.split("-")
            del hmap[key]
        else:
            key, value = instruction.split("=")
            hmap[key] = int(value)

    return hmap.focussing_powers()

assert answer_part1("test_input.txt") == 1320
assert answer_part1("real_input.txt") == 498538
assert answer_part2("test_input.txt") == 145
print(f"Answer to part 2 is {answer_part2('real_input.txt')}")

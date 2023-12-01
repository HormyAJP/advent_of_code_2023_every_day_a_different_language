#!/usr/bin/env python3

with open("./real_input.txt") as f:
    lines = [line.strip() for line in f.readlines()]

VALS = { "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6":6, "7": 7, "8": 8, "9": 9, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}

sum=0
for line in lines:
    if len(line) == 0:
        continue
    left=None
    for i in range(0, len(line)):
        for val in VALS.keys():
            if line[i:i+len(val)] == val:
                left = val
                break
        if left != None:
            break

    right=None
    for i in reversed(range(0, len(line))):
        for val in VALS.keys():
            if len(val) > len(line) - i:
                continue
            if line[i:i+len(val)] == val:
                right = val
                break
        if right != None:
            break

    number=f"{VALS[left]}{VALS[right]}"
    print(f"Got {number} from {line}")
    sum += int(number)
    print(f"Sum is now {sum}")
print(sum)

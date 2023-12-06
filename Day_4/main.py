#!/usr/bin/env python3

def read_file(filename):
    with open(filename) as f:
        lines = [line.strip() for line in f.readlines() if line.strip() != ""]
    return lines

def num_winning_numbers_on_card(winning_numbers, your_numbers):
    num_winning_numbers = 0
    for number in your_numbers:
        if number in winning_numbers:
            num_winning_numbers += 1

    return num_winning_numbers

def card_value(winning_numbers, your_numbers):
    num_winning_numbers = num_winning_numbers_on_card(winning_numbers, your_numbers)
    return 2 ** (num_winning_numbers - 1) if num_winning_numbers > 0 else 0

def parse_line(line):
    # Pushing my luck with the length of these comprehensions. For prod code I'd break them up.
    # Readability FTW!
    winning_numbers = [int(number) for number in line[line.index(":") + 1:line.index("|")].strip().split()]
    your_numbers = [int(number) for number in line[line.index("|") + 1:].strip().split()]
    return winning_numbers, your_numbers

def answer_part_1(filename):
    lines = read_file(filename)

    total = 0
    for line in lines:
        winning_numbers, your_numbers = parse_line(line)
        total += card_value(winning_numbers, your_numbers)
    return total

assert {answer_part_1('Day_4/test_input.txt') == 13}
print(f"Answer to Part 1 is {answer_part_1('Day_4/real_input.txt')}")

def answer_part_2(filename):
    lines = read_file(filename)

    num_cards = 0
    multipliers = [1] * len(lines)
    for iline, line in enumerate(lines):
        # Add the number of this card to the total
        num_cards += multipliers[iline]
        winning_numbers, your_numbers = parse_line(line)
        num_winning_numbers = num_winning_numbers_on_card(winning_numbers, your_numbers)
        for i in range(0, min(num_winning_numbers, len(lines) - iline)):
            # This is where the magic happens! We go theough the next N cards, where N is the
            # number of winning numbers for this card. We win one of each of those cards for each
            # of this card we have, i.e. we get another multipliers[iline] of each of the next N
            # cards.
            multipliers[i + iline + 1] += multipliers[iline]
    return num_cards

assert {answer_part_2('Day_4/test_input.txt') == 30}
print(f"Answer to Part 2 is {answer_part_2('Day_4/real_input.txt')}")
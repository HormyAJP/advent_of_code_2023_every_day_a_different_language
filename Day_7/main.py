#!/usr/bin/env python3

from enum import Enum
import functools

class Hand(Enum):
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    FULL_HOUSE = 4
    FOUR_OF_A_KIND = 5
    FIVE_OF_A_KIND = 6

def label_value(label, jacks_are_wild):
    if label == "A":
        return 14
    elif label == "K":
        return 13
    elif label == "Q":
        return 12
    elif label == "J":
        if jacks_are_wild:
            return 1
        else:
            return 11
    elif label == "T":
        return 10
    else:
        return int(label)

def type_of_hand_jacks_not_wild(hand):
    if len(set(hand)) == 1:
        return Hand.FIVE_OF_A_KIND
    elif len(set(hand)) == 2:
        if hand.count(hand[0]) in [1, 4]:
            return Hand.FOUR_OF_A_KIND
        else:
            return Hand.FULL_HOUSE
    elif len(set(hand)) == 3:
        for card in hand:
            match hand.count(card):
                case 1:
                    continue
                case 2:
                    return Hand.TWO_PAIR
                case 3:
                    return Hand.THREE_OF_A_KIND
                case _:
                    raise Exception(f"Logic error for {hand}")
    elif len(set(hand)) == 4:
        return Hand.PAIR
    else:
        return Hand.HIGH_CARD

def type_of_hand_jacks_are_wild(hand):
    num_jacks = hand.count("J")
    match num_jacks:
        case 0:
            return type_of_hand_jacks_not_wild(hand)
        case 1:
            match len(set(hand)):
                case 2:
                    # We have 1 jack and four of a kind, thus 5 of a kind
                    return Hand.FIVE_OF_A_KIND
                case 3:
                    # We have 1 jack, and two pairs or 1 jack, three of a kind and another distint
                    # card. We need to work harder to figure out which.
                    max_of_same_card = 0
                    for card in hand:
                        max_of_same_card = max(hand.count(card), max_of_same_card)
                    if max_of_same_card == 2:
                        return Hand.FULL_HOUSE
                    else:
                        return Hand.FOUR_OF_A_KIND
                case 4:
                    # We have 1 jack, a pair and three other distinct cards. So our best hand is 3
                    # of a kind
                    return Hand.THREE_OF_A_KIND
                case 5:
                    return Hand.PAIR
        case 2:
            match len(set(hand)):
                case 2:
                    # We have 2 jacks and three of a kind, thus 5 of a kind
                    return Hand.FIVE_OF_A_KIND
                case 3:
                    # We have 2 jacks, a pair and another card, thus 4 of a kind is our best hand
                    return Hand.FOUR_OF_A_KIND
                case 4:
                    # We have 2 jacks and three other distinct cards, thus 3 of a kind is our best hand
                    return Hand.THREE_OF_A_KIND
        case 3:
            if len(set(hand)) == 2:
                # We have 3 jacks and a pair, thus 5 of a kind
                return Hand.FIVE_OF_A_KIND
            else:
                # We have 3 jacks and two other different cards, thus 4 of a kind is our best hand.
                return Hand.FOUR_OF_A_KIND
        case 4 | 5:
            return Hand.FIVE_OF_A_KIND

def type_of_hand(hand, jacks_are_wild):
    return type_of_hand_jacks_are_wild(hand) if jacks_are_wild else type_of_hand_jacks_not_wild(hand)

def group_hands(hand_bid_pairs, jacks_are_wild):
    grouping = {}
    for hand_bid_pair in hand_bid_pairs:
        tpe = type_of_hand(hand_bid_pair[0], jacks_are_wild)
        grouping.setdefault(tpe, []).append(hand_bid_pair)
    return grouping

def compare_hand_bid_pairs_of_same_type(jacks_are_wild, hand_bid_pair1, hand_bid_pair2):
    hand1 = hand_bid_pair1[0]
    hand2 = hand_bid_pair2[0]
    for i in range(0, len(hand1)):
        left_value = label_value(hand1[i], jacks_are_wild)
        right_value = label_value(hand2[i], jacks_are_wild)
        # TODO: Can I access the default comparison operator for ints and just call that?
        if left_value < right_value:
            return -1
        elif left_value > right_value:
            return 1
        else:
            continue

def sort_hands_of_same_type(hand_bid_pairs, jacks_are_wild):
    comparison_function = functools.partial(compare_hand_bid_pairs_of_same_type, jacks_are_wild)
    return sorted(hand_bid_pairs, key=functools.cmp_to_key(comparison_function))

# Note: Passing jacks_are_wild all the way through the chain is pretty ugly. This could have been
# solved using OO or possibly with a bit more thought on function design. But AoC only gives you
# Part 2 once you've solved Part 1 and I didn't feel like massively refactoring this once I found
# out what Part 2 was.
# The only thing worth pointing out is that I only make jacks_are_wild optional at the top level. This
# prevents mistakes down the chain where I might forget to pass that value in. This is generally
# good practice. Beware of having an optional parameter all the way down your call hierarchy.
def compute_score(filename, jacks_are_wild=False):
    with open(filename) as f:
        hand_bid_pairs = [line.split() for line in f.readlines()]

    hand_groups = group_hands(hand_bid_pairs, jacks_are_wild)
    for type_, hand_bid_pairs in hand_groups.items():
        # N.B. You shouldn't really modify during iteration, but we're not going to change
        # the keys so this should be fine.
        hand_groups[type_] = sort_hands_of_same_type(hand_bid_pairs, jacks_are_wild=jacks_are_wild)

    rank = 1
    total_points = 0
    # Yuck. Making assumptions about the enum. Bit of a hack. Doesn't matter for AoC
    for i in range(Hand.HIGH_CARD.value, Hand.FIVE_OF_A_KIND.value + 1):
        for hand_bid_pair in hand_groups.get(Hand(i), []):
            total_points += int(hand_bid_pair[1]) * rank
            rank += 1
    return total_points

assert compute_score("test_input.txt") == 6440
assert compute_score("real_input.txt") == 250474325
assert compute_score("test_input.txt", jacks_are_wild=True) == 5905
print(f"Answer to part 2 is {compute_score('real_input.txt', jacks_are_wild=True)}")
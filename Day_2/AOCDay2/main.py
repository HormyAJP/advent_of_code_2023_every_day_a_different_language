#!/usr/bin/env python3

import re

with open("./AOCDay2/Resources/real_input.txt") as f:
    lines = [line.strip() for line in f.readlines()]

games = []
for i, line in enumerate(lines):
    game_tag = f"Game {i+1}: "
    if not line.startswith(game_tag):
        raise ValueError(f"Expected line {i} to start with 'Game {i}', but it didn't")
    line = line.replace(game_tag, "")
    games.append(line.split(";"))

def num_colour_per_draw(draw, colour):
    m = re.search(f"(\d+) {colour}", draw)
    if not m:
        return 0
    else:
        return int(m.group(1))

max_red = 12
max_green = 13
max_blue = 14
sum_ids = 0
for id, game in enumerate(games):
    bad_game = False
    for draw in game:
        num_red = num_colour_per_draw(draw, "red")
        num_green = num_colour_per_draw(draw, "green")
        num_blue = num_colour_per_draw(draw, "blue")

        if num_red > max_red or num_green > max_green or num_blue > max_blue:
            print(f"Game {id+1} is invalid due to draw {draw}")
            bad_game = True
            break
    if not bad_game:
        sum_ids += (id + 1)

print(f"Answer to part 1: {sum_ids}")
# 12 red cubes, 13 green cubes, and 14 blue cubes

sum_powers = 0
for id, game in enumerate(games):
    min_num_red = 0
    min_num_green = 0
    min_num_blue = 0

    for draw in game:
        num_red = num_colour_per_draw(draw, "red")
        num_green = num_colour_per_draw(draw, "green")
        num_blue = num_colour_per_draw(draw, "blue")

        min_num_blue = max(min_num_blue, num_blue)
        min_num_green = max(min_num_green, num_green)
        min_num_red = max(min_num_red, num_red)

    power = min_num_red * min_num_green * min_num_blue
    sum_powers += power

print(f"Answer to part 2: {sum_powers}")
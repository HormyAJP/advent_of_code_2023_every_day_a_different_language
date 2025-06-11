#!/usr/bin/env python3
import numpy as np
from enum import Enum

def parse_input(filename):
    with open(filename) as f:
        return np.array([list(line.strip()) for line in f.readlines()])

class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class BeamFront:

    def __init__(self, direction, coords):
        self.direction = direction
        self.coords = tuple(coords)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        match self.direction:
            case Direction.UP:
                return f"{self.coords} ^"
            case Direction.RIGHT:
                return f"{self.coords} >"
            case Direction.DOWN:
                return f"{self.coords} v"
            case Direction.LEFT:
                return f"{self.coords} <"
            case _:
                Exception(f"Unknown direction {self.direction}")

    def move(self, direction):
        match direction:
            case Direction.UP:
                return BeamFront(Direction.UP, [self.coords[0] - 1, self.coords[1]])
            case Direction.RIGHT:
                return BeamFront(Direction.RIGHT, [self.coords[0], self.coords[1] + 1])
            case Direction.DOWN:
                return BeamFront(Direction.DOWN, [self.coords[0] + 1, self.coords[1]])
            case Direction.LEFT:
                return BeamFront(Direction.LEFT, [self.coords[0], self.coords[1] - 1])
            case _:
                Exception(f"Unknown direction {direction}")

def beam_hits_tile(beam_front, tile):
    match tile:
        case ".":
            return [beam_front.move(beam_front.direction)]
        case "-":
            if beam_front.direction in [Direction.UP, Direction.DOWN]:
                return [beam_front.move(Direction.LEFT), beam_front.move(Direction.RIGHT)]
            else:
                return [beam_front.move(beam_front.direction)]
        case "|":
            if beam_front.direction in [Direction.LEFT, Direction.RIGHT]:
                return [beam_front.move(Direction.UP), beam_front.move(Direction.DOWN)]
            else:
                return [beam_front.move(beam_front.direction)]
        case "\\":
            match beam_front.direction:
                case Direction.UP:
                    return [beam_front.move(Direction.LEFT)]
                case Direction.RIGHT:
                    return [beam_front.move(Direction.DOWN)]
                case Direction.DOWN:
                    return [beam_front.move(Direction.RIGHT)]
                case Direction.LEFT:
                    return [beam_front.move(Direction.UP)]
        case "/":
            match beam_front.direction:
                case Direction.UP:
                    return [beam_front.move(Direction.RIGHT)]
                case Direction.RIGHT:
                    return [beam_front.move(Direction.UP)]
                case Direction.DOWN:
                    return [beam_front.move(Direction.LEFT)]
                case Direction.LEFT:
                    return [beam_front.move(Direction.DOWN)]
        case _:
            raise Exception(f"Unknown tile {tile}")

def tile_was_energized(directions):
    return 1 if any(directions) else 0

def num_energized_tiles_given_starting_beam(grid, start_beam):
    # Create a grid for tracking what direction of beams we've seen at each
    # tile. That's a 2D array of 4-element arrays.
    directions_seen = np.full(grid.shape + (4,), fill_value=False, dtype=bool)
    current_beam_fronts = [start_beam]
    directions_seen[start_beam.coords][start_beam.direction.value] = True

    while len(current_beam_fronts):
        new_beam_fronts = []

        for beam_front in current_beam_fronts:
            new_beam_fronts += beam_hits_tile(beam_front, grid[beam_front.coords])

        beams_for_next_step = []
        for new_beam_front in new_beam_fronts:
            if new_beam_front.coords[0] < 0 or new_beam_front.coords[0] >= len(grid):
                continue
            if new_beam_front.coords[1] < 0 or new_beam_front.coords[1] >= len(grid[0]):
                continue
            if directions_seen[new_beam_front.coords][new_beam_front.direction.value]:
                continue
            directions_seen[new_beam_front.coords][new_beam_front.direction.value] = True
            beams_for_next_step.append(new_beam_front)
        current_beam_fronts = beams_for_next_step

    counts = np.apply_along_axis(tile_was_energized, 2, directions_seen)
    return np.sum(counts)

def answer_part_1(filename):
    grid = parse_input(filename)
    start_beam = BeamFront(Direction.RIGHT, [0,0])
    return num_energized_tiles_given_starting_beam(grid, start_beam)

def answer_part_2(filename):
    grid = parse_input(filename)
    max_energized_tiles = 0
    start_beams = []
    for i in range(0, len(grid)):
        # Add start beams for left hand side
        start_beams.append(BeamFront(Direction.RIGHT, [i, 0]))
        # Add start beams for right hand side
        start_beams.append(BeamFront(Direction.LEFT, [i, len(grid[0]) - 1]))
    for j in range(0, len(grid[0])):
        # Add start beams for top
        start_beams.append(BeamFront(Direction.DOWN, [0, j]))
        # Add start beams for bottom
        start_beams.append(BeamFront(Direction.UP, [len(grid) - 1, j]))

    for start_beam in start_beams:
        max_energized_tiles = max(max_energized_tiles, num_energized_tiles_given_starting_beam(grid, start_beam))
    return max_energized_tiles

assert answer_part_1("test_input.txt") == 46
assert answer_part_1("real_input.txt") == 7482
assert answer_part_2("test_input.txt") == 51
print(f"Answer to part 2 is {answer_part_2('real_input.txt')}")

#!/usr/bin/env ruby

require 'matrix'

module Tile
  NONE = '.'
  VERTICAL = '|'
  HORIZONTAL = '-'
  TOP_LEFT = 'F'
  TOP_RIGHT = '7'
  BOTTOM_LEFT = 'L'
  BOTTOM_RIGHT = 'J'
  START = 'S'
end

def assert(truthy)
  if !truthy
    raise "Assertion failed"
  end
end

def prettify_tile(tile)
  case tile
  when Tile::NONE
    " "
  when Tile::VERTICAL
    "║"
  when Tile::HORIZONTAL
    "═"
  when Tile::TOP_LEFT
    "╔"
  when Tile::TOP_RIGHT
    "╗"
  when Tile::BOTTOM_LEFT
    "╚"
  when Tile::BOTTOM_RIGHT
    "╝"
  when Tile::START
    "S"
  else
    raise "Unknown tile #{tile}"
  end
end

def parse_input(filename)
    File.readlines(filename).map(&:strip).map(&:chars)
end

def pretty_print_path(grid, path)
    pretty = Matrix.build(grid.length, grid[0].length) { "░" }
    path.each do |index|
      pretty[index[0], index[1]] = prettify_tile(grid[index[0]][index[1]])
    end
    pretty
  end

def pretty_print_right_hand_side_of_loop(pretty_grid, indices)
  indices.each do |index|
    pretty_grid[index[0], index[1]] = 'R'
  end
end

def start_position(grid)
  grid.each_with_index do |row, irow|
      row.each_with_index do |tile, icol|
          return [irow, icol] if tile == Tile::START
      end
  end
  raise "No start position found"
end

def all_directions_from_grid_entry(index)
  next_directions_from_grid_entry(Tile::HORIZONTAL, index) +
    next_directions_from_grid_entry(Tile::VERTICAL, index)
end

def next_directions_from_grid_entry(tile, start)
  case tile
  when Tile::VERTICAL
    [[start[0] + 1, start[1]], [start[0] - 1, start[1]]]
  when Tile::HORIZONTAL
    [[start[0], start[1] + 1], [start[0], start[1] - 1]]
  when Tile::TOP_LEFT
    [[start[0], start[1] + 1], [start[0] + 1, start[1]]]
  when Tile::TOP_RIGHT
    [[start[0], start[1] - 1], [start[0] + 1, start[1]]]
  when Tile::BOTTOM_LEFT
    [[start[0], start[1] + 1], [start[0] - 1, start[1]]]
  when Tile::BOTTOM_RIGHT
    [[start[0], start[1] - 1], [start[0] - 1, start[1]]]
  when Tile::START, Tile::NONE
    []
  else
    raise "Unknown tile #{tile}"
  end
end

def index_is_in_grid(index, grid)
  index[0] >= 0 && index[0] < grid.length && index[1] >= 0 && index[1] < grid[0].length
end

def path_is_a_loop(grid, loop_entries, current)
  previous = loop_entries[0]
  while current != loop_entries[0]
    type_ = grid[current[0]][current[1]]
    next_steps = next_directions_from_grid_entry(type_, current)
    return false if next_steps.empty? || !next_steps.include?(previous)

    next_steps.delete(previous)
    loop_entries << current
    previous, current = current, next_steps[0]
  end

  true
end

def compute_start_loop(grid)
  start = start_position(grid)
  next_locations = [
    [start[0] + 1, start[1]],
    [start[0], start[1] + 1],
    [start[0] - 1, start[1]],
    [start[0], start[1] - 1]
  ]

  next_locations.each do |next_location|
    next if next_location[0] < 0 || next_location[0] >= grid.length
    next if next_location[1] < 0 || next_location[1] >= grid[0].length

    loop_entries = [start]
    if path_is_a_loop(grid, loop_entries, next_location)
      return loop_entries
    end
  end
  raise "No loop found"
end

def indices_to_the_right(current, next_, next_type)
  ret = []
  if current[0] == next_[0]
    if current[1] < next_[1]
      ret << [next_[0] + 1, next_[1]]
      ret << [next_[0], next_[1] + 1] if next_type == Tile::BOTTOM_RIGHT
    else
      ret << [next_[0] - 1, next_[1]]
      ret << [next_[0], next_[1] - 1] if next_type == Tile::TOP_LEFT
    end
  elsif current[1] == next_[1]
    if current[0] < next_[0]
      ret << [next_[0], next_[1] - 1]
      ret << [next_[0] + 1, next_[1]] if next_type == Tile::BOTTOM_LEFT
    else
      ret << [next_[0], next_[1] + 1]
      ret << [next_[0] - 1, next_[1]] if next_type == Tile::TOP_RIGHT
    end
  else
    raise "Can't find index to the right of #{current} and #{next_}"
  end
  ret
end

# Test cases for indices_to_the_right
all_test_tiles_of_interest = [Tile::VERTICAL, Tile::HORIZONTAL, Tile::TOP_LEFT, Tile::TOP_RIGHT, Tile::BOTTOM_LEFT, Tile::BOTTOM_RIGHT]
# Test moving right
test_tiles = all_test_tiles_of_interest.dup
test_tiles.delete(Tile::BOTTOM_RIGHT)
test_tiles.each do |test_tile|
    assert(indices_to_the_right([10, 10], [10, 11], test_tile) == [[11, 11]])
end
assert(indices_to_the_right([10, 10], [10, 11], Tile::BOTTOM_RIGHT) == [[11, 11], [10, 12]])
# Test moving left
test_tiles = all_test_tiles_of_interest.dup
test_tiles.delete(Tile::TOP_LEFT)
test_tiles.each do |test_tile|
    assert(indices_to_the_right([10, 10], [10, 9], test_tile) == [[9, 9]])
end
assert(indices_to_the_right([10, 10], [10, 9], Tile::TOP_LEFT) == [[9, 9], [10, 8]])

# TODO: Translate these tests
# # Test moving Down
# test_tiles = copy(all_test_tiles_of_interest)
# test_tiles.remove(Tile.BOTTOM_LEFT)
# for test_tile in test_tiles:
#     assert indices_to_the_right((10, 10), (11, 10), test_tile) == [(11, 9)]
# assert indices_to_the_right((10, 10), (11, 10), Tile.BOTTOM_LEFT) == [(11, 9), (12, 10)]
# # Test moving Up
# test_tiles = copy(all_test_tiles_of_interest)
# test_tiles.remove(Tile.TOP_RIGHT)
# for test_tile in test_tiles:
#     assert indices_to_the_right((10, 10), (9, 10), test_tile) == [(9, 11)]
# assert indices_to_the_right((10, 10), (9, 10), Tile.TOP_RIGHT) == [(9, 11), (8, 10)]

def find_all_squares_to_the_immediate_right_of_the_loop(grid, loop)
  loop_copy = loop.dup << loop[0]

  right_hand_side_of_loop = []
  (0...loop_copy.length - 1).each do |i|
    indices = indices_to_the_right(loop_copy[i], loop_copy[i+1], grid[loop_copy[i+1][0]][loop_copy[i+1][1]])
    indices.each do |index|
      next if loop_copy.include?(index) || !index_is_in_grid(index, grid)

      right_hand_side_of_loop << index
    end
  end
  right_hand_side_of_loop
end

def flood(grid, loop, index)
  flooded_indices = [index]
  next_indices_to_fill_from = [index]
  until next_indices_to_fill_from.empty?
    next_indices_to_fill_from_in_next_loop = []
    next_indices_to_fill_from.each do |next_index|
      all_directions_from_grid_entry(next_index).each do |index|
        next if flooded_indices.include?(index) || !index_is_in_grid(index, grid) || loop.include?(index)

        flooded_indices << index
        next_indices_to_fill_from_in_next_loop << index
      end
    end
    next_indices_to_fill_from = next_indices_to_fill_from_in_next_loop
  end
  flooded_indices
end

def flood_fill(grid, loop, indices_to_flood)
  flooded_indices = []
  indices_to_flood.uniq.each do |index|
    next if flooded_indices.include?(index)

    flooded_indices.concat(flood(grid, loop, index))
  end
  flooded_indices
end

def answer_part_1(filename)
  grid = parse_input(filename)
  loop = compute_start_loop(grid)
  loop.length / 2
end

def answer_part_2(filename)
  grid = parse_input(filename)
  loop = compute_start_loop(grid)

  flood_start_indices = find_all_squares_to_the_immediate_right_of_the_loop(grid, loop)
  flooded_indices = flood_fill(grid, loop, flood_start_indices)
  # pretty = pretty_print_path(grid, loop)
  # pretty_print_right_hand_side_of_loop(pretty, flooded_indices)
  # pretty.to_a.each do |row|
  #   puts row.join("")
  # end

  [flooded_indices.length, grid.length * grid[0].length - flooded_indices.length - loop.length]
end

assert(answer_part_1("./test_input1.txt") == 4)
assert(answer_part_1("./test_input2.txt") == 8)
assert(answer_part_1("./real_input.txt") == 6697)
assert(answer_part_2("./test_input3.txt").include? 4)
assert(answer_part_2("./test_input4.txt").include? 8)
assert(answer_part_2("./test_input5.txt").include? 10)
assert(answer_part_2("./real_input.txt").include? 423)

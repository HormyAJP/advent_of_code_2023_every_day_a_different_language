#!/usr/bin/env pwsh

# NOTE: Part 2 of this code doesn't work. There are bugs. I need to write tests to find them. My
# coding standards are inconsistent as well. That needs tidying afterwards. I should probably
# break up the code into different files as well.

# Exit script on first error
$ErrorActionPreference = "Stop"

# Uncomment this line to show debugging
# $DebugPreference = "Continue"

function assert-equal {
    <#
        .SYNOPSIS
            Asserts that two objects are equal. If they are not, prints an error message and exits
            with a non-zero exit code.
    #>
    param(
        [Parameter(Mandatory=$true)]
        [System.Object]$actual,

        [Parameter(Mandatory=$true)]
        [System.Object]$expected
    )

    # Use Compare-Object so that this works with arrays as well as scalars.
    if ($(Compare-Object $actual $expected)) {
        Write-Error "Expected '$expected' but got '$actual'"
        exit 1
    }
}

# This class exists purely so I can return multiple values from a function. Not clear to me what
# best practices are here yet.
class InputData {
    [System.Array]$seeds
    [hashtable]$maps
}

function parse_input_data {
    <#
        .SYNOPSIS
            A grotty parser. Makes a lot of assumptions about input data and doesn't have a lot
            of error checking.
    #>
    param(
        [string]$inputFilePath
    )

    $regex1 = '^seeds: (.*)$'
    $regex2 = '^([^\s]+) map:$'
    $regex3 = '^(\d+) (\d+) (\d+)$'

    $all_maps = @{}
    $current_map = ""
    Get-Content $inputFilePath | ForEach-Object {
        # TODO: What is $_?
        $line = $_

        # Check against the first regex
        if ($line -match $regex1) {
            # Check if the $seedsArray variable is already defined
            if ($seeds) {
                # Print to stderr then exit
                Write-Error "Error: found 'seeds: xxx' line twice"
                exit 1
            }

            # Get group 1 from regex match
            $seedsString = $matches[1]
            # Split the $seeds string by whitespace into an array
            $seeds = $seedsString -split '\s+'
            # Convert each element of the seedsArray to an integer
            $seeds = $seeds | ForEach-Object { [System.Int64]$_ }
        }
        elseif ($line -match $regex2) {
            $current_map = $matches[1]
            $all_maps[$current_map] = New-Object System.Collections.ArrayList
        }
        elseif ($line -match $regex3) {
            $all_maps[$current_map].Add(@([System.Int64]$matches[1], [System.Int64]$matches[2], [System.Int64]$matches[3]))
        }
    }

    $ret = [InputData]::new()
    $ret.seeds = $seeds
    $ret.maps = $all_maps
    return $ret
}

function map_key_for_category {
    param(
        # TODO: What's the default?
        [Parameter(Mandatory=$true)]
        [string]$category,

        [Parameter(Mandatory=$true)]
        [hashtable]$allMaps
    )

    $categoryRegex = "$category-to-.*"
    foreach ($key in $allMaps.Keys) {
        if ($key -match $categoryRegex) {
            return $key
        }
    }

    throw "No map found for category $category"
}

function next_value_from_maps {
    param(
        [Parameter(Mandatory=$true)]
        [System.Int64]$value,

        [Parameter(Mandatory=$true)]
        [System.Collections.ArrayList]$maps
    )

    foreach ($map in $maps) {
        if ($map[1] -le $value -and $value -le $map[1] + $map[2]) {
            return $value + $map[0] - $map[1]
        }
    }
    return $value
}

assert-equal $(next_value_from_maps -value 123 -maps @(@(456, 123, 1),@(0, 0, 0))) 456
assert-equal $(next_value_from_maps -value 123 -maps @(@(1, 1, 1),@(0, 0, 0))) 123

function location_from_seed {
    param(
        [Parameter(Mandatory=$true)]
        [Int64]$seed,

        [Parameter(Mandatory=$true)]
        [hashtable]$maps
    )
    Write-Debug "Processing seed $seed"
    $current_category = "seed"
    $current_value = $seed

    do {
        $map_key = map_key_for_category -category $current_category -allMaps $maps
        $next_value = next_value_from_maps $current_value $maps[$map_key]
        $current_category = ($map_key -split '-')[2]
        Write-Debug "Mapped $current_value to $next_value. Next category is $current_category"
        $current_value = $next_value

    } while ($current_category -ne "location")

    return $next_value
}

$test_maps = @{
    "seed-to-xxx" = @(@(1, 1, 1), (0,0,0))
    "xxx-to-location" = @(@(1, 1, 1), (0,0,0))
}
assert-equal $(location_from_seed 123 $test_maps) 123

$test_maps = @{
    "seed-to-xxx" = @(@(123, 123, 1), (0,0,0))
    "xxx-to-location" = @(@(456, 123, 1), (0,0,0))
}
assert-equal $(location_from_seed 123 $test_maps) 456

function find_minimum_location_from_seeds {
    param(
        [Parameter(Mandatory=$true)]
        [Int64[]]$seeds,

        [Parameter(Mandatory=$true)]
        [hashtable]$maps
    )

    $min_location = [System.Int64]::MaxValue

    foreach ($seed in $seeds) {
        $min_location = [math]::Min($min_location, $(location_from_seed $seed $maps))
    }
    return $min_location
}

function answer_part1 {
    param(
        [string]$inputFilePath
    )
    $inputData = parse_input_data $inputFilePath

    return find_minimum_location_from_seeds $inputData.seeds $inputData.maps
}

# I needed to write a custom iterator because our seed ranges can be massive. I can't use
# the built-in range operator A..B because that generates all elements up front (shame they don't
# do what Python does and lazy generate.
class SeedGenerator : System.Collections.IEnumerator {
    [Int64]$start
    [Int64]$end
    [Int64]$next

    SeedGenerator([Int64]$start, [Int64]$count) {
        $this.start = $start - 1
        $this.end = $start + $count - 1 # TODO
        $this.Reset();
    }

    [object] get_Current() {
        return $this.next
    }

    [bool] MoveNext() {
        $this.next++
        return $this.next -le $this.end
    }

    [void] Reset() {
        $this.next = $this.start
    }
}

# Quick tests for my custom iterator
assert-equal @([SeedGenerator]::new(0, 0)) @()
assert-equal @([SeedGenerator]::new(0, 1)) @(0)
assert-equal @([SeedGenerator]::new(5, 10)) @(5..14)

function seeds_to_seed_generators {
    param(
        [Parameter(Mandatory=$true)]
        [System.Array]$seeds
    )

    $seed_generators = New-Object System.Collections.ArrayList
    # Iterate an integer from 0 to length of $seeds and increment by 2
    for ($i = 0; $i -lt $seeds.Length; $i += 2) {
        [void]$seed_generators.Add([SeedGenerator]::new($seeds[$i], $seeds[$i+1]))
    }
    return $seed_generators
}

# This was my first cut. It simply isn't going to work. The computation takes too long! 🤦‍♂️
function bad_answer_part2 {
    param(
        [string]$inputFilePath
    )
    $inputData = parse_input_data $inputFilePath

    $min_location = [System.Int64]::MaxValue
    $seed_generators = seeds_to_seed_generators $inputData.seeds
    foreach ($seed_generator in $seed_generators) {
        Write-Debug "Processing seed generator..."
        foreach ($seed in $seed_generator) {
            $min_location = [math]::Min($min_location, $(location_from_seed $seed $inputData.maps))
        }
    }

    return $min_location
}

assert-equal $(answer_part1 -inputFilePath "./test_input.txt") 35
$part1_answer = $(answer_part1 -inputFilePath "./real_input.txt")
Write-Host "Answer to part 1 is $part1_answer"
# Turn this into a test case in case I break things
assert-equal $part1_answer 910845529

function seeds_to_intervals {
    param(
        [Parameter(Mandatory=$true)]
        $seeds
    )

    $intervals = New-Object System.Collections.ArrayList
    for ($i = 0; $i -lt $seeds.Length - 1; $i += 2) {
        Write-Host $($seeds[0]).GetType().FullName
        $bottom = $($seeds[$i]) + $($seeds[$i+1]) - 1
        [void]$intervals.Add(@($seeds[$i], $bottom))
    }
    return $intervals
}

# function range_intersection

function maps_to_domains {
    param(
        $maps
    )
    $domains = New-Object System.Collections.ArrayList
    foreach ($map in $maps) {
        $bottom = $map[1] + $map[2] - 1
        [void]$domains.Add(@($map[1], $bottom))
    }
    return $domains
}

function interval_intersection_and_complements {
    param(
        $top_interval,
        $bot_interval
    )

    $ret = New-Object System.Collections.ArrayList

    $start = [math]::Max($top_interval[0], $bot_interval[0])
    $end = [math]::Min($top_interval[1], $bot_interval[1])
    if ($start -gt $end) {
        # If there's no intersection then we can't break up the interval any smaller.
        [void]$ret.Add($top_interval)
        return ,$ret
    }
    $intersection = @($start, $end)
    [void]$ret.Add($intersection)

    if ($top_interval[0] -lt $bot_interval[0]) {
        # Handle these cases:
        # Case 1
        # [       ]
        #     [       ]
        # Case 2
        # [         ]
        #     [    ]
        [void]$ret.Add(@($top_interval[0], $bot_interval[0] - 1))
        if ($top_interval[1] -le $bot_interval[1]) {
            [void]$ret.Add(@($bot_interval[0], $top_interval[1]))
        } else {
            [void]$ret.Add(@($bot_interval[0], $bot_interval[1]))
            [void]$ret.Add(@($bot_interval[1] + 1, $top_interval[1]))
        }
    } else {
        # Handle these cases:
        # Case 1
        #     [    ]
        # [           ]
        # Case 2
        #     [       ]
        # [       ]

        if ($top_interval[1] -lt $bot_interval[1]) {
            [void]$ret.Add($top_interval)
        } else {
            [void]$ret.Add(@($top_interval[0], $bot_interval[1]))
            [void]$ret.Add(@($bot_interval[1] + 1, $top_interval[1]))
        }
    }

    return $ret
}

function clever_shit {
    param(
        $accessibleIntervals,
        $maps
    )

    $slicedIntervals = New-Object System.Collections.ArrayList
    # We can think of maps as functions whose domains are intervals and whose
    # ranges are intervals. We first get the domain of all the maps.
    $domains = maps_to_domains $maps
    # We then break up our input intervals into the same granularity as the maps to the next
    # intervals, e.g.
    # Current Intervals:     [     ]       [        ]
    # Domains of maps:   [      ]       [      ]  [     ]
    # Result:            [   ][ ][ ]
    foreach ($interval in $accessibleIntervals) {
        foreach ($domain in $domains) {
            $ret = $(interval_intersection_and_complements $interval $domain)
            [void]$slicedIntervals.AddRange($ret)
        }
    }

    # No we know that all our accessible intervals have been broken up into smaller intervals
    # which will be entirely contained in one of the maps domains or entirely disjoin. We can
    # more easily iterate through now and map those intervals to the intervals they map to.

    $mappedIntervals = New-Object System.Collections.ArrayList
    foreach ($interval in $slicedIntervals) {
        $found = false
        # Remember that maps are of the form [DESTINATION, SOURCE, LENGTH]
        foreach ($map in $maps) {
            if ($interval[0] -ge $map[1] -and $interval[1] -le $map[1] + $map[2] - 1) {
                $found = true
                # Map the interval to it's new interval
                $bottom = $interval[0] + $map[0] - $map[1]
                $top = $interval[1] + $map[0] - $map[1]
                [void]$mappedIntervals.Add(@($bottom, $top))
            }
        }
        if (-not $found) {
            # If there's no mapping then the interval just preserves its value.
            [void]$mappedIntervals.Add($interval)
        }
    }

    return $mappedIntervals
}

function answer_part2 {
    param(
        [string]$inputFilePath
    )
    $inputData = parse_input_data $inputFilePath
    $accessibleIntervals = seeds_to_intervals $inputData.seeds

    # Write-Debug "Processing seed $seed"
    $current_category = "seed"
    # $current_value = $seed

    do {
        $map_key = map_key_for_category -category $current_category -allMaps $inputData.maps
        $accessibleIntervals = clever_shit $accessibleIntervals $inputData.maps[$map_key]
        $current_category = ($map_key -split '-')[2]
        Write-Debug " Next category is $current_category"
    } while ($current_category -ne "location")

    # Now all we need to do is find the minimum left endpoint of the intervals

    $min_location = [System.Int64]::MaxValue
    foreach ($interval in $accessibleIntervals) {
        $min_location = [math]::Min($min_location, $interval[0])
    }
    return $min_location
}

assert-equal $(answer_part2 -inputFilePath "./test_input.txt") 46
# Write-Host "Answer to part 2 is $(answer_part2 -inputFilePath "./real_input.txt")"



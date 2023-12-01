#!/usr/bin/env bash

# "Debug mode" [grimace]
# set -x

assert() {
    if [[ $1 != $2 ]]; then
        echo @>&1 "ERROR: Expected $2 got $1"
        exit 1
    fi
}

sum_of_calibration_values_from_input_file_part_1() {
    input_lines=()
    while IFS=$'\n' read line; do
        input_lines+=($line)
    done < $1

    sum=0
    for line in "${input_lines[@]}"
    do
        regex="^[^0-9]*([0-9]).*"
        if [[ $line =~ $regex ]]
        then
            fist_digit="${BASH_REMATCH[1]}"
        else
            echo @>&1 "ERROR: Could not find first digit in the string $line using regex $regex"
            exit 1
        fi

        regex="^.*([0-9])[^0-9]*"
        if [[ $line =~ $regex ]]
        then
            last_digit="${BASH_REMATCH[1]}"
        else
            echo @>&1 "ERROR: Could not find last digit in the string $line using regex $regex"
            exit 1
        fi

        two_digit_number=$fist_digit$last_digit
        # For debugging:
        # echo "Got $two_digit_number from $line"
        sum=$((sum + $two_digit_number))
    done

    echo $sum
}

# Test case
assert $(sum_of_calibration_values_from_input_file_part_1 "test_input_part1.txt") 142
output=$(sum_of_calibration_values_from_input_file_part_1 "real_input.txt")
echo "Answer to part 1 is $output"

# It would have been nice to use an associative array here but my version of bash doesn't support
# them [cry]
NUMBER_STRINGS=("1" "2" "3" "4" "5" "6" "7" "8" "9" "one" "two" "three" "four" "five" "six" "seven" "eight" "nine")

index_of() {
    needle=$1
    haystack=("${@:2}")
    for (( i = 0; i < ${#haystack[@]}; i++ )); do
        if [[ ${haystack[$i]} == $needle ]]; then
            echo $i
            return
        fi
    done
}

leftmost_number_in_string() {
    str=$1
    for (( i = 0; i < ${#str}; i++ )); do
        for number in "${NUMBER_STRINGS[@]}"; do
            length=${#number}
            # For debugging:
            # echo "Searching for '$number' in $str at position $i. Substring is '${str:$i:$length}'"
            if [[ ${str:$i:$length} == $number ]]; then
                # For debugging:
                # echo "Found leftmost number $number in string $str"
                if [[ $length == 1 ]]; then
                    echo $number
                    return
                fi
                index=$(index_of $number "${NUMBER_STRINGS[@]}")
                echo $(( index - 8 ))
                return
            fi
        done
    done
    echo 2>&1 "ERROR: Could not find leftmost number in string $str"
}

rightmost_number_in_string() {
    str=$1
    for (( i = ${#str} - 1; i >= 0; i-- )); do
        for number in "${NUMBER_STRINGS[@]}"; do
            length=${#number}
            # For debugging:
            # echo "Searching for '$number' in $str at position $i. Substring is '${str:$i:$length}'"
            if [[ ${str:$i:$length} == $number ]]; then
                # For debugging:
                # echo "Found rightmost number $number in string $str"
                if [[ $length == 1 ]]; then
                    echo $number
                    return
                fi
                index=$(index_of $number "${NUMBER_STRINGS[@]}")
                echo $(( index - 8 ))
                return
            fi
        done
    done
    echo 2>&1 "ERROR: Could not find rightmost number in string $str"
}

sum_of_calibration_values_from_input_file_part_2() {
    input_lines=()
    while read line; do
        input_lines+=($line)
    done < $1

    sum=0
    for line in "${input_lines[@]}"
    do
        fist_digit=$(leftmost_number_in_string $line)
        last_digit=$(rightmost_number_in_string $line)
        two_digit_number=$fist_digit$last_digit
        sum=$((sum + $two_digit_number))
    done

    echo $sum
}

# Test cases
assert $(leftmost_number_in_string 1) 1
assert $(rightmost_number_in_string 1) 1
assert $(leftmost_number_in_string 186) 1
assert $(rightmost_number_in_string 186) 6
assert $(leftmost_number_in_string onerbfkf4threeone) 1
assert $(rightmost_number_in_string onerbfkf4threeone) 1
assert $(leftmost_number_in_string hbfr9mm) 9
assert $(rightmost_number_in_string hbfr9mm) 9
assert $(leftmost_number_in_string bcmqn9onecnrzhsrsgzggzhtskjeightbz6khfhccktwonenrj) 9
assert $(rightmost_number_in_string bcmqn9onecnrzhsrsgzggzhtskjeightbz6khfhccktwonenrj) 1
assert $(rightmost_number_in_string asdsad4thre) 4
assert $(leftmost_number_in_string six) 6
assert $(rightmost_number_in_string six) 6
assert $(leftmost_number_in_string 9jdxljkfqttstqxdzdsztsxrfjbkqmmsqzseven) 9
assert $(rightmost_number_in_string 9jdxljkfqttstqxdzdsztsxrfjbkqmmsqzseven) 7
assert $(sum_of_calibration_values_from_input_file_part_2 "test_input_part2.txt") 281

output=$(sum_of_calibration_values_from_input_file_part_2 "real_input.txt")
echo "Answer to part 2 is $output"

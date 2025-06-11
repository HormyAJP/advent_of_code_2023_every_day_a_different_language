#!/usr/bin/env bash

echo "Hello"

# for WORD in `cat test_input.txt`
# do
#    echo $WORD
# done

# arr=()
# IFS=$'\n'
# for line in `cat test_input.txt`; do
#     echo "PARKER: $line"
#     arr[${#arr[@]}]=$line
# done

readarray -t input_lines < real_input.txt

sums=()

sum=0
for value in "${input_lines[@]}"
do
    if [ "$value" == "" ];
    then
        sums+=($sum)
        sum=0
    else
        sum=$(($sum + $value))
    fi
done
sums+=($sum)

# Elves are numbered starting at 1
index=0
max_index=0
max=0
for v in ${sums[@]}; do
    index=$((index+1))
    if (( $v > $max ))
    then
        max=$v
        max_index=$index
    fi
done

echo "MAX: $max at $max_index"



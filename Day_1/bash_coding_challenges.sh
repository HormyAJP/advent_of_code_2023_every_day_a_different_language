#!/usr/bin/env bash

# Ideas for exercises taken from here: https://www.codecademy.com/resources/blog/bash-script-code-challenges-for-beginners/

# LEARN: Make it an error to access unbound variables. This even picks up array overruns.
set -u

# LEARN: Parameter expansion:
# The ‘$’ character introduces parameter expansion, command substitution, or arithmetic expansion.
# The parameter name or symbol to be expanded may be enclosed in braces, which are optional but
# serve to protect the variable to be expanded from characters immediately following it which could
# be interpreted as part of the name.
FOO="foo"
# This will evaluate to the value of FOO concatendated with "x". If we didn't use braces
# then we'd be trying to expand the variable FOOx
echo ${FOO}x > /dev/null


# if [ x$VAR = "xvalue" ]; then
#     echo $VAR
# fi

# PATH="/usr/local/"
# for f in '/usr/local/*'; do echo $f; done
# for f in '/usr/local/*'; do echo "$f"; done
# for f in '$PATH*'; do echo "$f"; done
# for f in $PATH*; do echo "$f"; done


# variable="Some string"
# variable = "Some string"
# variable= "Some string"

ap_list_directory() {
    if [[ $# != 1 ]]; then
        # TODO: How to get the function name dynamically? FUNCNAME didn't work.
        >&2 echo "ap_list_directory accepts exactly one parameter"
        >&2 echo "Usage: TODO"
        # LEARN: We return 1 rather than exit 1 here because this script should be sources and
        # thus exiting would exit the users current shell
        return 1
    fi

    # Name the variable for clarity
    PATH_TO_LIST=$1
    # LEARN: How to slice a variable. Here we are saying "start at -1 and give me everything after
    # that" Note that the brackets around the -1 are required
    if [[ ${PATH_TO_LIST:(-1)} != "/" ]]; then
        PATH_TO_LIST=${PATH_TO_LIST}/
    fi
    # LEARN: Applying for to a path just lists the directory
    for f in ${PATH_TO_LIST}*; do
        echo $f
    done
}

ap_pick_your_favourite() {
    VALID_INPUT=false
    echo "Which would you choose: cake, pudding or fruit?"

    # LEARN: How to handle booleans. Note that false and true aren't special. They are just strings.
    # You could equally use "talse" and "frue".
    while [[ $VALID_INPUT == false ]]; do
        # LEARN: Read from stdin
        read RESPONSE1
        # LEARN: How to handle case statements
        case "$RESPONSE1" in
            cake|pudding|fruit)
                VALID_INPUT=true
                echo "Okay, what type of $RESPONSE1 would you like?"
                ;; # LEARN: Double semi-conlons are just the way the syntax is :shrug:
                # LEARN: You can do fallthrough, but it's a bit sketchy. Check out ;& and ;;&.
            *)
                echo "That's not a valid choice. Please try again."
                ;;
        esac
    done
    read RESPONSE2
    echo "Yum! You're getting a $RESPONSE2 $RESPONSE1!"
}

# TODO: Can I prevent this being exported by sourcing?
_ap_list_directory_with_sort_condition() {
    if [[ $# != 2 ]]; then
        >&2 echo "_ap_list_directory_with_sort_condition accepts exactly two parameters"
        return 1
    fi

    PATH_TO_LIST=$1
    SORT_CONDITION=$2
    if [[ ${PATH_TO_LIST:(-1)} != "/" ]]; then
        PATH_TO_LIST=${PATH_TO_LIST}/
    fi

    contents=()
    for f in ${PATH_TO_LIST}*; do
        contents+=($f)
    done

    # echo $contents[@]

    if [[ $SORT_CONDITION == "asc" ]]; then
        IFS=$'\n' sorted_contents=($(sort <<<"${contents[*]}"))
        unset IFS
    elif [[ $SORT_CONDITION == "desc" ]]; then
        IFS=$'\n' sorted_contents=($(sort -r <<<"${contents[*]}"))
        unset IFS
    else
        # LEARN: Copying an array is messy. If you try to do something like sorted_contents=$contents
        # then you'll get a string with all the elements concatenated together. Instead you need to
        # unpack then array and then surrpose it by brackets to tell bash to form a new array with
        # the same contents. Note also that you must use @ not * in the array expansion. The difference
        # bettwen @ and * is that @ expands to each element of the array as a separate word, whereas
        # * creates a single word (including white space) with all the elements concatenated together.
        # That means that bash will then just create an array of one word.
        sorted_contents=( "${contents[@]}" )
    fi

    message="\nContents of ${PATH_TO_LIST}"
    echo $message
    printf '=%.0s' {1..${#message}}
    printf '\n'

    for f in $sorted_contents; do
        echo $f
    done
}

ap_list_and_sort_directories() {
    # LEARN: The input paramter array is represented by $@. You can access members directly using
    # $0,.. $9. For anything beyond the 10th value you need to use ${@[n]}. Note that this applies
    # whether you're in a function or at the top level of the script.

    asc_desc=none
    for value in $@; do
        case "$value" in
            a)
                asc_desc=asc
                ;;
            d)
                asc_desc=desc
                ;;
            *)
                _ap_list_directory_with_sort_condition $value $asc_desc
        esac
    done
}

# TODO: How does $0, $1 work? How to get the correspjnding array? How to detect num of vars
# echo PARKER: $0
echo $@

# LEARN: How to check for being sourced
# LEARN: How to access an element of an array
# LEARN: -n means string is not empty (-z means it's empty, think "zero")
# LEARN: +x means that we use the string "x if BASH_SOURCE is set but use the empty string is
# BASH_SOURCE is unset". The trick here is that we don't want
if [[ -n ${BASH_SOURCE+x} && ${BASH_SOURCE[0]} == $0 ]]; then
    # LEARN: How to redirect to stderr:
    >&2 echo "This script should not be run directly. Source it instead to add functionality to your current environment"
    # exit 1
fi


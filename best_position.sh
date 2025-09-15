#!/bin/bash

readonly NUM_GAMES=100000000

# Check that there's an arg
if [ "$#" -ne 1 ]; then
    echo "Please provide a number of players."
    exit 1
fi

# Check that the arg is an int
re='^[0-9]+$'
if ! [[ "$1" =~ $re ]] ; then
    echo "Please provide a number of players."
    exit 1
fi

function max_index {
    local index=0
    local max=${}
}

# Simulate 10M games
lcr-sim/target/release/lcr-sim --games $NUM_GAMES --players $1 -s | awk 'NR == 1 || $1 > max {number = NR; max = $1} END {if (NR) print number}'
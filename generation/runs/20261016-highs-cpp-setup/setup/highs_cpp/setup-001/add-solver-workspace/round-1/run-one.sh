#!/bin/sh
# Compile models/PROBLEM.cpp against the image's HiGHS and run it on one instance.
# Usage: run-one.sh PROBLEM INSTANCE_JSON
set -e
problem="$1"; shift
g++ -std=c++17 -O2 "/m/$problem.cpp" -o "/tmp/$problem" -I/opt/highs/include/highs -L/opt/highs/lib -lhighs -lpthread
"/tmp/$problem" "$@"

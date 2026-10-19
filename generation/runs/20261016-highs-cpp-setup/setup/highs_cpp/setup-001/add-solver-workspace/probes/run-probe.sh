#!/bin/sh
# Compile and run a probe program against the installed HiGHS, inside the image.
# Usage: run-probe.sh NAME [extra args]   (NAME.cpp in the same folder)
set -e
cd /p
name="$1"; shift
g++ -std=c++17 -O1 -I/opt/highs/include/highs "$name.cpp" -o "$name" -L/opt/highs/lib -lhighs -lpthread
"./$name" "$@"

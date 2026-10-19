#!/bin/sh
# Build and run one skill example in a scratch copy, inside the image.
# Usage: run-example.sh EXAMPLE_NAME
set -e
rm -rf /tmp/ex && mkdir -p /tmp/ex && cp -r /skill/assets/"$1"/. /tmp/ex/ && cd /tmp/ex
export HIGHS_PREFIX=/opt/highs
g++ -std=c++17 -O2 model.cpp -o model -I"$HIGHS_PREFIX/include/highs" -L"$HIGHS_PREFIX/lib" -lhighs -lpthread
./model

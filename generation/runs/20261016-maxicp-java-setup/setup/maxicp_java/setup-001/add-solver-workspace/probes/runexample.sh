#!/bin/sh
# usage: runexample.sh EXAMPLE_DIR "java File.java args"
# Runs one skill example in the maxicp_java image, as check_assets does, and shows its output.
EXAMPLE=$1
CMD=$2
PROBE=/home/tias/research/kostis/DCP-Bench-Open/.claude/worktrees/maxicp-java/generation/runs/20261016-maxicp-java-setup/setup/maxicp_java/setup-001/add-solver-workspace/probes
docker run --rm -e "CLASSPATH=${CP:-/jars/maxicp-0.0.3.jar:/jars/gson-2.11.0.jar}" \
  -v "$PROBE/maven:/jars:ro" -v "$EXAMPLE:/w" -w /w --entrypoint sh dcp-eval/maxicp_java:v1 -c "$CMD"

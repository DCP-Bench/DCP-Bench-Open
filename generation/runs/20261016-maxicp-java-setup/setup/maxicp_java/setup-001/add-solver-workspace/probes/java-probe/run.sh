#!/bin/sh
# usage: run.sh MainClass File1.java [File2.java ...]
# Compiles the probe sources and runs MainClass inside the Java image. Nothing runs on the host.
PROBE=/home/tias/research/kostis/DCP-Bench-Open/.claude/worktrees/maxicp-java/generation/runs/20261016-maxicp-java-setup/setup/maxicp_java/setup-001/add-solver-workspace/probes
MAIN=$1; shift
docker run --rm -v "$PROBE/maven:/jars:ro" -v "$PROBE/java-probe:/w" -w /w eclipse-temurin:21-jdk-noble \
  sh -c "javac -encoding UTF-8 -nowarn -cp /jars/maxicp-0.0.3.jar:/jars/gson-2.11.0.jar -d /tmp/out $* && java -cp /tmp/out:/jars/maxicp-0.0.3.jar:/jars/gson-2.11.0.jar $MAIN"

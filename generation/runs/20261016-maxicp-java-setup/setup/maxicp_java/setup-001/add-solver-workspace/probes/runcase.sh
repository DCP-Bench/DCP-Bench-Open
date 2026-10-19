#!/bin/sh
# usage: runcase.sh CASE_DIR
# CASE_DIR holds model.java and request.json; they are mounted at /input of the maxicp_java image.
# The image runs with no network and a read-only root, as in evaluation.
CASE=$1
docker run --rm --network none --read-only --tmpfs /tmp:rw,size=512m --memory 2g \
  -v "$CASE:/input:ro" dcp-eval/maxicp_java:v1

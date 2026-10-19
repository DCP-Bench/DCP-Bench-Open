#!/bin/bash
set -x
docker build -f /home/tias/research/kostis/DCP-Bench-Open/.claude/worktrees/mip-python/generation/runs/20261016-mip-python-setup/setup/mip_cbc/probes/Dockerfile.probe -t dcp-probe/mip_cbc:2.0.0 /home/tias/research/kostis/DCP-Bench-Open/.claude/worktrees/mip-python/generation/runs/20261016-mip-python-setup/setup/mip_cbc/probes 2>&1

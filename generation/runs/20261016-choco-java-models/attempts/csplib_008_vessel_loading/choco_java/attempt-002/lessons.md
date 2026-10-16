The output convention decides acceptance: left/bottom are lower edges and right/top exclusive upper edges (top = bottom + length). Inclusive ends, and width/length swapped on the axes, were rejected by the evaluator.
The reference allows 90-degree turns (tiling_rotation needs them). Element over {width, length} with a boolean turned flag works.
With a rotated model, inputOrder or minDom timed out on the 16x16 instances. domOverWDeg with Luby restarts solved json:1 in 24 s and json:2 in 1.4 s.

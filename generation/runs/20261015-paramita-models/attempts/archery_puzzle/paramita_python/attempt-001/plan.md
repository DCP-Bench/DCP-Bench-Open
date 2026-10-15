# Plan: archery_puzzle (Paramita)

- The young archer shoots as many arrows as she pleases at 6 targets, the hits on each target are counted -> hits[i] in 0..H_i as unary Bools ge[i][k] (k=1..H_i), hits[i] = sum(ge[i]); H_i = (target_score + max target - 1) // targets[i] (bound from optimality: an optimal total is below target_score + max target).
- "how close can she come to scoring the target score" -> total = sum over i of targets[i] * hits[i] (weighted sum of the unary Bools).
- Deviation above the target -> overshoot p = unary Bools, total - target <= p, width max(targets).
- Deviation below the target -> undershoot n = unary Bools, target - total <= n, width target_score.
- Objective: minimize p + n (equals |total - target| at optimum).
- Output hits: list of the six hits[i] sums.

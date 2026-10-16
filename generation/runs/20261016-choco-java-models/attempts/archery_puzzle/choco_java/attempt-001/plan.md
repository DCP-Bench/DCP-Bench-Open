# Plan: archery score as close as possible to the target (archery_puzzle)

- "using as many arrows as she pleases, on targets with ring scores targets_i" -> hits_i = m.intVarArray(0..bound_i), bound_i = floor(2T / targets_i)
- "total score = sum of hits_i times the ring score" -> m.scalar(hits, targets, "=", total)
- "how close to the target score T" -> deviation = |total - T|: diff = total - T, dev = m.absolute(diff)
- bound on total: zero arrows gives deviation T, so the optimum has deviation <= T and total <= 2T (sound, from the instance)
- "minimise the deviation" -> setObjective(MINIMIZE, dev)
- "print hits per target" -> output hits

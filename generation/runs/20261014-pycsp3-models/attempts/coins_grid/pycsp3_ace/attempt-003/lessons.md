attempt-001 (plain 0/1 grid, row and column sums, z = sum of (i-j)^2) accepted 4 of 5 instances; the 12x12 json:4 hit execution_timeout (skipped, not a pass).
attempt-002 (per-row and per-column cost variables, bounds from the c cheapest cells) did not help: json:4 still execution_timeout, 'Candidate optimum was not proven'.
attempt-003 adds LexIncreasing([row-major grid, transposed grid]) (transpose symmetry, same cost); all 5 instances then proven and accepted in one evaluation.

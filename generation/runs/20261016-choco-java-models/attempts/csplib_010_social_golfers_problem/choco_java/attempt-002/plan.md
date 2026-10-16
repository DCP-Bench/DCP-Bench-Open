# Plan: social golfers (csplib_010), attempt 2

- golfers = n_groups * group_size (derived from instance), weeks = n_weeks, groups = n_groups
- each golfer plays once a week in one group -> assign[i][w] in 0..n_groups-1
- every group in a week holds exactly group_size golfers -> globalCardinality(column of week w, values 0..G-1, occ = group_size, closed)
- groups are interchangeable within a week (symmetry, not a rule of the problem) -> intValuePrecedeChain on each week's column
- no two golfers share a group on more than one occasion -> per pair i<j, reified together[w] = (assign[i][w] = assign[j][w]), sum <= 1
- objective -> none (satisfaction); output assign = assign
- search: domOverWDeg on all assign variables, Luby restarts (attempt 1 timed out on instances with 15-25 golfers)

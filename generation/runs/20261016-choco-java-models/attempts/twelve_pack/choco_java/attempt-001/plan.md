Given a target number of items -> instance field target, read via inst.getInt("target")
find the closest combination of packs of different sizes -> counts[i] = number of packs of size packs[i], IntVars
that meets or exceeds the target -> sum of counts[i] * packs[i] >= target
closest -> minimise total = sum counts[i] * packs[i] (the excess over the target)
Print the counts of each pack size used (counts) -> out.put("counts", counts)
Objective: minimize total

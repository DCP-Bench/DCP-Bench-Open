Attempt 001 was accepted on n = 7 and n = 15 but hit the 180 s execution budget
on n = 9 and n = 13. The model is unchanged in attempt 002; only the labelling
order is, to [ff, down]. Each row of this problem needs exactly three of its n
Booleans set, so trying 1 before 0 commits to a triple immediately instead of
ruling out one cell at a time, and the constraint set is identical either way.

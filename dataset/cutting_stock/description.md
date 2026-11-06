This is a cutting stock problem. Raw rolls have a width `roll_width`, and pieces of several smaller widths are cut
from them: `orders[i]` pieces of width `widths[i]` are needed. There are `num_patterns` cutting patterns, and
cutting one raw roll with pattern `i` yields `num_rolls_width[i][j]` pieces of width `widths[j]`. The problem aims to
minimize the total number of raw rolls cut, while at least the ordered number of pieces of each width is produced.
How many rolls should be cut using each pattern?

Print the number of times each cutting pattern is used (patterns_used) as a list of integers, and the total number of raw rolls cut (min_rolls_cut) as an integer.

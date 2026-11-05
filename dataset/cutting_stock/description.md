This is a cutting stock problem. Given a roll of width `RollWidth` and a set of widths to be cut. Each width
has a certain number of Orders. There are `NumPatterns` patterns and each pattern has a certain number
of rolls of each width. The problem aims to minimize the total number of raw rolls cut. It is
constrained that for each width, the total number of rolls cut meets the total Orders. How to decide the number of
rolls cut using each patter?

Print the number of times each cutting pattern is used (patterns_used) as a list of integers, and the total number of raw rolls cut (min_rolls_cut) as an integer.

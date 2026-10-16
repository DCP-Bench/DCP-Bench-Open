start with [0]; each step adds 5, adds 7, or takes sqrt -> table over (x[i-1], x[i]) of allowed transitions (sqrt only for perfect squares)
all elements are distinct -> allDifferent(x, "AC")
all elements are <= 60 and integers -> domains 0..60
list starts with 0 -> x[0] = 0
list ends with 14 -> x[23] = 14
sequence length 24 -> 24 variables
2, 10 and 14 appear on the list in that order -> seen2[i] = 2 appeared at or before i; is10[j] => seen2[j-1]; 2 seen by index 22; some 10 at index <= 22
objective: none (satisfaction); output x[24]

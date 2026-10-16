Joe's account number has all digits 0..n-1 in some order -> x is a permutation of 0..n-1: allDifferent(x, "AC") with domains 0..n-1
In each set just k digits are in their correct position -> for each set, the number of positions i with x[i] = set[i] equals k: a Boolean per position (x[i] = set[i]) and sum(bools) = k
Print the account number as a list of n integers -> output x
Objective: none (satisfaction)

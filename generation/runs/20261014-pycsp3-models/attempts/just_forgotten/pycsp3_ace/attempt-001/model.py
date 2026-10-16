from pycsp3 import *

# Just forgotten: the account number holds the digits 0 to n-1 in some order.
# Each recorded set is a permutation of the digits, and in each set exactly k digits
# are in the same position as in the account number.
sets = data.sets
k = data.num_correct_digits
n = len(sets[0])

# x[i] is the digit at position i of the account number
x = VarArray(size=n, dom=range(n))

satisfy(
    # every digit from 0 to n-1 appears exactly once
    AllDifferent(x),
    # in each set, exactly k digits are in their correct position
    [Sum(x[i] == sets[t][i] for i in range(n)) == k for t in range(len(sets))],
)

from pycsp3 import *

# The set {1, 3, 8, 120} has the property that the product of any two of its integers is one less
# than a perfect square. Find a fifth number, at least 0, that keeps this property.
MAX_VAL = data.max_val
known = [1, 3, 8, 120]

# number is the fifth number
number = Var(dom=range(0, MAX_VAL + 1))

# root[k] is the square root of (known[k] * number + 1), so that the product plus one is a square
root = VarArray(size=len(known), dom=range(0, 1100))

satisfy(
    # the product of each known integer with the fifth number is one less than a perfect square
    [root[k] * root[k] == known[k] * number + 1 for k in range(len(known))],
)

from pycsp3 import *

# select elements of the collection that sum to zero
n = len(data.nums)
# indices[i] is 1 if element i is selected
indices = VarArray(size=n, dom={0, 1})
satisfy(
    # the number of selected elements is m
    Sum(indices) == data.m,
    # the selected elements sum to zero
    Sum(data.nums[i] * indices[i] for i in range(n)) == 0,
)

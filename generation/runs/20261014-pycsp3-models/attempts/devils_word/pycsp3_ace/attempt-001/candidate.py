from pycsp3 import *

# put a plus or a minus sign before each number so that the signed sum is the total
n = len(data.arr)
arr = data.arr

# result[i] is arr[i] with its sign, so it is either arr[i] or -arr[i]
result = VarArray(size=n, dom=range(-max(arr), max(arr) + 1))

satisfy(
    # each number of the array gets a plus or a minus sign
    [Table(scope=[result[i]], supports=[(arr[i],), (-arr[i],)]) for i in range(n)],
    # the signed numbers add up to the total
    Sum(result) == data.total,
)

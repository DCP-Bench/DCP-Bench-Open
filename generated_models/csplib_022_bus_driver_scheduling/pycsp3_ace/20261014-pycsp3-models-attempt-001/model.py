from pycsp3 import *

# Bus driver scheduling: choose a set of shifts that covers each piece of work exactly once,
# using as few shifts as possible. Each shift covers a subset of the tasks.
num_work = data.num_work
num_shifts = data.num_shifts
shifts = data.shifts

# x[s] is 1 when shift s is selected
x = VarArray(size=num_shifts, dom={0, 1})

satisfy(
    # each piece of work is covered by exactly one selected shift
    [Sum(x[s] for s in range(num_shifts) if t in shifts[s]) == 1 for t in range(num_work)],
)

# the total number of shifts used is as small as possible
minimize(Sum(x))

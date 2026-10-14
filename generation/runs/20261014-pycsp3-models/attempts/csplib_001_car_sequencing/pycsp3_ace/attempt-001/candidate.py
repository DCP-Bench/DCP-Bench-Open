# Problem: Order the cars so that no option station is overloaded in any window of consecutive slots.
from pycsp3 import *

demand = data.demand
requires = data.requires
at_most = data.at_most
per_slots = data.per_slots
C = len(demand)
O = len(at_most)
L = sum(demand)
# sequence[p] is the car type in slot p
sequence = VarArray(size=L, dom=range(C))
# has[p][o] = 1 if the car in slot p requires option o
has = VarArray(size=[L, O], dom={0, 1})
satisfy(
    # each car type is built as many times as it is demanded
    [Count(sequence, value=c) == demand[c] for c in range(C)],
    # the options of the car in each slot agree with its car type
    [Table(scope=[sequence[p]] + list(has[p]), supports=[(c,) + tuple(requires[c]) for c in range(C)]) for p in range(L)],
    # in every window of per_slots[o] consecutive slots, at most at_most[o] cars need option o
    [Sum(has[p + k][o] for k in range(per_slots[o])) <= at_most[o] for o in range(O) for p in range(L - per_slots[o] + 1)],
)

# Five people (Baker, Cooper, Fletcher, Miller, Smith) live on the first five
# floors of an apartment house, one person per floor. Floors are numbered 1..5.
# Each person's floor is one-hot: pf[person][v] is true when that person lives
# on floor v. Integer floor numbers are sums of these Bools.
from paramita.modelling import Bool

FLOORS = range(1, 6)
PEOPLE = ["B", "C", "F", "M", "S"]


def build(instance):
    fl = {p: {v: Bool(f"floor_{p}_{v}") for v in FLOORS} for p in PEOPLE}
    floor = {p: sum(v * fl[p][v] for v in FLOORS) for p in PEOPLE}
    cons = []

    # every person lives on exactly one floor
    for p in PEOPLE:
        cons.append(sum(fl[p].values()) == 1)

    # they all live on different floors: each floor holds at most one person
    for v in FLOORS:
        cons.append(sum(fl[p][v] for p in PEOPLE) == 1)

    # Baker does not live on the fifth floor
    cons.append(~fl["B"][5])

    # Cooper does not live on the first floor
    cons.append(~fl["C"][1])

    # Fletcher does not live on either the fifth or the first floor
    cons.append(~fl["F"][5])
    cons.append(~fl["F"][1])

    # Miller lives on a higher floor than does Cooper
    cons.append(floor["M"] >= floor["C"] + 1)

    # Smith does not live on a floor adjacent to Fletcher's
    for v in range(1, 5):
        cons.append(~(fl["S"][v] & fl["F"][v + 1]))
        cons.append(~(fl["S"][v + 1] & fl["F"][v]))

    # Fletcher does not live on a floor adjacent to Cooper's
    for v in range(1, 5):
        cons.append(~(fl["F"][v] & fl["C"][v + 1]))
        cons.append(~(fl["F"][v + 1] & fl["C"][v]))

    outputs = {p: floor[p] for p in PEOPLE}
    return cons, outputs

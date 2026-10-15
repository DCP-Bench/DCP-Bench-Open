# Twelve-pack problem: choose how many packs of each size to use so that the
# number of beers meets or exceeds the target, and the number is as close to
# the target as possible.

from paramita.modelling import Bool, If


def build(instance):
    packs = instance["packs"]      # beers in one pack of each size
    target = instance["target"]    # the number of beers needed

    # The number of packs of size i is encoded in unary: ge[i][k] is true when
    # at least k + 1 packs of size i are used.
    # Bound: an optimal solution never uses more than ceil(target / size)
    # packs of one size, because dropping one such pack would still reach the
    # target and lower the total. The bound comes from the instance fields.
    ge = []
    for i, p in enumerate(packs):
        ub = -(-target // p)
        ge.append([Bool(f"ge_{i}_{k}") for k in range(ub)])

    cons = []

    # a count of at least k + 1 packs needs a count of at least k packs
    for row in ge:
        cons += [If(row[k + 1], row[k]) for k in range(len(row) - 1)]

    # the total number of beers (sum of packs times count) meets or exceeds the target
    # one row of the total per pack size, each row a sum of its unary bits
    rows = [sum(p * b for b in row) for p, row in zip(packs, ge)]
    total = sum(rows)
    cons.append(total >= target)

    # output: the number of packs used of each size is the sum of its unary bits
    counts = [sum(row) for row in ge]

    # objective: the total number of beers, to be minimised, so the closest
    # combination that still reaches the target is chosen
    return cons, {"counts": counts}, ("minimize", total)

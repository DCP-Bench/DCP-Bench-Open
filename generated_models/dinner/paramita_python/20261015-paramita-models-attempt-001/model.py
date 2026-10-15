# Dinner party: choose how many grandparents, parents and children go to dinner.
# Integers are unary counts: each count is 1 + the number of true Bools in an
# order chain (the chain makes the Bools a prefix, so the sum is the count).
# Unary is used because the counts are summed and weighted, not matched.
from paramita.modelling import Bool, If


def unary(name, count):
    # count-1 ordered Bools; bits[i] true means the value is at least i+2
    bits = [Bool(f"{name}_ge_{i + 2}") for i in range(count - 1)]
    return bits


def build(instance):
    # The problem statement fixes the ranges: 1-6 grandparents, 1-10 parents,
    # 1-40 children, 20 people in total, and a bill of exactly $20.
    max_gp, max_par, max_ch = 6, 10, 40
    people, budget_half_dollars = 20, 40  # cost in half-dollars: $20 = 40 halves

    gs = unary("gp", max_gp)
    ps = unary("par", max_par)
    cs = unary("ch", max_ch)

    cons = []

    # the chain: a higher count implies every lower count
    for bits in (gs, ps, cs):
        for i in range(len(bits) - 1):
            cons.append(If(bits[i + 1], bits[i]))

    grandparents = sum(gs) + 1
    parents = sum(ps) + 1
    children = sum(cs) + 1

    # there must be 20 total people at dinner
    cons.append(grandparents + parents + children == people)

    # it must cost $20: grandparents $3 (6 halves), parents $2 (4 halves), children $0.50 (1 half)
    cons.append(6 * grandparents + 4 * parents + children == budget_half_dollars)

    outputs = {"grandparents": grandparents, "parents": parents, "children": children}
    return cons, outputs

# Mario's gold route: Mario drives from his house to Luigi's house, visiting houses
# to collect gold, within a fuel limit. Maximise the gold collected.
from paramita.modelling import Bool, If, Iff, Or


def build(instance):
    n = instance["nHouses"]
    mario = instance["marioHouse"]
    luigi = instance["luigiHouse"]
    fuel = instance["arc_fuel"]
    gold = instance["goldInHouse"]
    fuel_limit = instance["fuelLimit"]
    houses = range(n)

    # arc[i][j]: Mario drives straight from house i to house j (one-hot successor encoding).
    # Arcs out of Luigi's house go only to Mario's house, and only Luigi's house enters Mario's house.
    arc = [[None] * n for _ in houses]
    for i in houses:
        for j in houses:
            if i == j:
                continue
            if (i == luigi) != (j == mario):
                continue
            # an arc that alone uses more fuel than the limit can never be driven
            if fuel[i][j] > fuel_limit:
                continue
            arc[i][j] = Bool(f"arc_{i}_{j}")

    def out_arcs(i):
        return [arc[i][j] for j in houses if arc[i][j] is not None]

    def in_arcs(j):
        return [arc[i][j] for i in houses if arc[i][j] is not None]

    # visited[i]: house i is on the route (it has an outgoing arc). Gold is collected per visited house.
    visited = [Bool(f"visited_{i}") for i in houses]

    # pos[(i, k)]: house i is at least k stops after Mario's house (unary order encoding of the stop number).
    pos = {(i, k): Bool(f"pos_{i}_ge_{k}") for i in houses for k in range(1, n)}

    cons = []

    # a house is on the route exactly when it has an outgoing arc (at most one, see below)
    cons += [Iff(visited[i], Or(out_arcs(i))) for i in houses]

    # the order bits of one house form a prefix: at least k+1 stops implies at least k stops
    for i in houses:
        cons += [If(pos[(i, k + 1)], pos[(i, k)]) for k in range(1, n - 1)]
    # Mario's house is the first stop, at position 0
    cons += [~pos[(mario, k)] for k in range(1, n)]

    # Mario starts his route: one outgoing arc from Mario's house
    cons.append(sum(out_arcs(mario)) == 1)
    # Luigi's succeeding house is Mario's house
    cons.append(sum(out_arcs(luigi)) == 1)
    # the route ends at Luigi's house: exactly one arc enters it, and Mario's house is only entered from Luigi's house
    cons.append(sum(in_arcs(luigi)) == 1)
    cons.append(sum(in_arcs(mario)) == 1)

    # a visited house is entered once and left once, never visited twice
    for i in houses:
        if i in (mario, luigi):
            continue
        cons.append(sum(out_arcs(i)) == sum(in_arcs(i)))
        cons.append(sum(out_arcs(i)) <= 1)
        cons.append(sum(in_arcs(i)) <= 1)

    # the route has no side loops away from Mario: along each travelled arc (i, j) the stop number grows
    # by at least one, so no cycle can form without Mario's house (the closing arc Luigi -> Mario is excluded)
    for i in houses:
        for j in houses:
            a = arc[i][j]
            if a is None or j == mario:
                continue
            cons.append(If(a, pos[(j, 1)]))
            if i != mario:
                for k in range(1, n - 1):
                    cons.append(If(a, If(pos[(i, k)], pos[(j, k + 1)])))
                cons.append(If(a, ~pos[(i, n - 1)]))

    # the fuel used on the travelled arcs must not exceed the fuel limit
    cons.append(sum(fuel[i][j] * arc[i][j] for i in houses for j in houses if arc[i][j] is not None) <= fuel_limit)

    # the succeeding house of house i: the house it drives to, or i itself when the house is not on the route
    s = [i + sum((j - i) * arc[i][j] for j in houses if arc[i][j] is not None) for i in houses]

    # total gold collected: the gold of each house on the route
    total_gold = sum(gold[i] * visited[i] for i in houses)

    return cons, {"s": s}, ("maximize", total_gold)

# Mario's gold route: Mario starts at his house, visits some houses and ends at
# Luigi's house, using at most a given amount of fuel, and wants to collect as
# much gold as possible. The route is given by the successor of each house on it
# (a house off the route is its own successor), and Luigi's successor is Mario.
import functools
import operator

from hermax.model import Model


def build(instance):
    n = instance["nHouses"]
    mario = instance["marioHouse"]
    luigi = instance["luigiHouse"]
    fuel_limit = instance["fuelLimit"]
    arc_fuel = instance["arc_fuel"]  # arc_fuel[i][j] = fuel to drive from house i to house j
    gold = instance["goldInHouse"]

    m = Model()
    # s[i] = the house after house i on the route; s[i] = i when house i is not visited
    s = m.int_vector("s", n, 0, n - 1)
    # next_to[i][j] = the successor of house i is house j (one-hot form of s)
    next_to = m.bool_matrix("next_to", n, n)
    for i in range(n):
        m &= next_to.row(i).exactly_one()
        for j in range(n):
            m &= (~next_to[i][j] | (s[i] == j))

    # All successors are different (every house is the successor of exactly one
    # house; houses off the route are their own successors).
    for j in range(n):
        m &= next_to.col(j).exactly_one()

    # The route ends at Luigi's house, which leads back to Mario's house.
    m &= next_to[luigi][mario]

    # rank[i][r - 1] = house i is the r-th stop of the route, counting from 1 at
    # Mario's house. Ranks are all different (a permutation of 1..n), Mario has rank 1.
    rank = m.bool_matrix("rank", n, n)
    for i in range(n):
        m &= rank.row(i).exactly_one()
        m &= rank.col(i).exactly_one()
    m &= rank[mario][0]

    # Rank progression: a house on the route, other than the one that leads back
    # to Mario, is followed by the house with the next rank. This also rules out
    # separate cycles apart from the one through Mario.
    for i in range(n):
        for j in range(n):
            if i != j and j != mario:
                for r in range(n - 1):
                    m &= (~next_to[i][j] | ~rank[i][r] | rank[j][r + 1])
                m &= (~next_to[i][j] | ~rank[i][n - 1])  # nothing follows the last rank

    # Rank segregation: a house off the route ranks after Luigi's house.
    for i in range(n):
        if i != luigi:
            for a in range(n):
                for b in range(a + 1):
                    m &= (~next_to[i][i] | ~rank[luigi][a] | ~rank[i][b])

    # the fuel used by the route is at most the limit; an arc that is longer
    # than the whole limit can never be driven
    for i in range(n):
        for j in range(n):
            if arc_fuel[i][j] > fuel_limit:
                m &= ~next_to[i][j]
    m &= (sum(arc_fuel[i][j] * next_to[i][j] for i in range(n) for j in range(n)
              if arc_fuel[i][j] > 0) <= fuel_limit)

    # Maximise the gold collected from the visited houses (s[i] != i). The total
    # forgone gold is paid for the houses left out: a house is left out when
    # next_to[i][i] holds, and a soft clause on its negation pays then.
    for i in range(n):
        if gold[i] > 0:
            m.obj[gold[i]] += ~next_to[i][i]

    return m, {"s": s}

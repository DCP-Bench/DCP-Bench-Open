# Travelling salesman problem: find the shortest tour that visits every city exactly once and returns
# to the start; the distance between two cities is their Euclidean distance rounded to an integer.
# The declared output is the length of the shortest tour.
import math
from itertools import combinations

from exact import Exact


def build(instance):
    locations = instance["locations"]
    n_city = len(locations)

    # distance between every pair of cities: Euclidean distance rounded to an integer
    distance = [[0 if i == j else int(round(math.hypot(locations[i][0] - locations[j][0],
                                                       locations[i][1] - locations[j][1])))
                 for j in range(n_city)] for i in range(n_city)]

    # An upper bound for the shortest tour: the length of a tour found by going to the nearest
    # unvisited city and then improving it with 2-opt moves. Any tour is an upper bound, so the
    # shortest tour is never longer than this; it only narrows the search.
    tour = [0]
    while len(tour) < n_city:
        last = tour[-1]
        tour.append(min((c for c in range(n_city) if c not in tour), key=lambda c: distance[last][c]))
    improved = n_city > 3
    while improved:
        improved = False
        for a in range(1, n_city - 1):
            for b in range(a + 1, n_city):
                before = distance[tour[a - 1]][tour[a]] + distance[tour[b]][tour[(b + 1) % n_city]]
                after = distance[tour[a - 1]][tour[b]] + distance[tour[a]][tour[(b + 1) % n_city]]
                if after < before:
                    tour[a:b + 1] = reversed(tour[a:b + 1])
                    improved = True
    upper = sum(distance[tour[k]][tour[(k + 1) % n_city]] for k in range(n_city))

    solver = Exact()

    # go[i][j] = 1 if the tour travels from city i directly to city j (j is visited right after i)
    go = [[f"go_{i}_{j}" if i != j else None for j in range(n_city)] for i in range(n_city)]
    for i in range(n_city):
        for j in range(n_city):
            if i != j:
                solver.addVariable(go[i][j], 0, 1)

    # every city is left exactly once and entered exactly once (a successor circuit)
    for i in range(n_city):
        solver.addConstraint([(1, go[i][j]) for j in range(n_city) if j != i],
                             True, 1, True, 1)
        solver.addConstraint([(1, go[j][i]) for j in range(n_city) if j != i],
                             True, 1, True, 1)

    # The arcs must form one circuit, not several small ones. Exact has no circuit constraint, so
    # every city except city 0 gets a visiting order order[i] in 1..n-1 (city 0 is the start), and
    # an arc i -> j between two such cities forces order[j] >= order[i] + 1 (the
    # Miller-Tucker-Zemlin constraint): a loop that avoids city 0 would need order to increase
    # around it, which is impossible. Written in the lifted form of Desrochers and Laporte,
    # order[i] - order[j] + (n-1) * go[i][j] + (n-3) * go[j][i] <= n-2, which is also valid when the
    # opposite arc is used and is tighter than the plain form.
    order = [None] + [f"order_{i}" for i in range(1, n_city)]
    for i in range(1, n_city):
        solver.addVariable(order[i], 1, n_city - 1)
    if n_city > 2:
        for i in range(1, n_city):
            for j in range(1, n_city):
                if i != j:
                    terms = [(1, order[i]), (-1, order[j]), (n_city - 1, go[i][j])]
                    if n_city > 3:  # the lifting coefficient n-3 is 0 for three cities
                        terms.append((n_city - 3, go[j][i]))
                    solver.addConstraint(terms, False, 0, True, n_city - 2)
        # no loop through two cities
        for i, j in combinations(range(n_city), 2):
            solver.addConstraint([(1, go[i][j]), (1, go[j][i])], False, 0, True, 1)
    if n_city > 3:
        # no loop through any three cities (implied by the order constraints; stated directly they
        # propagate as soon as the arcs are chosen)
        for i, j, k in combinations(range(n_city), 3):
            solver.addConstraint([(1, go[a][b]) for a in (i, j, k) for b in (i, j, k) if a != b],
                                 False, 0, True, 2)

    # travel_distance = the total length of the tour
    solver.addVariable("travel_distance", 0, upper)
    solver.addConstraint([(distance[i][j], go[i][j]) for i in range(n_city)
                          for j in range(n_city) if i != j and distance[i][j]]
                         + [(-1, "travel_distance")], True, 0, True, 0)
    # every city is left through some arc, so the tour is at least the sum over cities of the
    # shortest arc leaving it (implied; it gives the solver a starting lower bound)
    solver.addConstraint([(1, "travel_distance")], True,
                         sum(min(distance[i][j] for j in range(n_city) if j != i)
                             for i in range(n_city)) if n_city > 1 else 0)

    # minimise the travelled distance
    return solver, {"travel_distance": "travel_distance"}, ("minimize", [(1, "travel_distance")])

# Travelling salesman problem: find the shortest tour that visits every city exactly once and returns
# to the start; the distance between two cities is their Euclidean distance rounded to an integer.
# The declared output is the length of the shortest tour.
import math

from exact import Exact


def build(instance):
    locations = instance["locations"]
    n_city = len(locations)

    # distance between every pair of cities: Euclidean distance rounded to an integer
    distance = [[0 if i == j else int(round(math.hypot(locations[i][0] - locations[j][0],
                                                       locations[i][1] - locations[j][1])))
                 for j in range(n_city)] for i in range(n_city)]

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
    # around it, which is impossible. Written as order[i] - order[j] + (n-1) * go[i][j] <= n-2.
    order = [None] + [f"order_{i}" for i in range(1, n_city)]
    for i in range(1, n_city):
        solver.addVariable(order[i], 1, n_city - 1)
    for i in range(1, n_city):
        for j in range(1, n_city):
            if i != j:
                solver.addConstraint([(1, order[i]), (-1, order[j]), (n_city - 1, go[i][j])],
                                     False, 0, True, n_city - 2)
    # two cities cannot be a loop of their own (implied for more than two cities; it propagates
    # earlier than the order constraints)
    if n_city > 2:
        for i in range(n_city):
            for j in range(i + 1, n_city):
                solver.addConstraint([(1, go[i][j]), (1, go[j][i])], False, 0, True, 1)

    # travel_distance = the total length of the tour
    total = sum(max(row) for row in distance)
    solver.addVariable("travel_distance", 0, total)
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

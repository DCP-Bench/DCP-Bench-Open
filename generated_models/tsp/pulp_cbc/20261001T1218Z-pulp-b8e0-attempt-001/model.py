"""Travelling salesman: given the locations of cities, find the shortest route that visits
every city exactly once and returns to the city it started from. The distance between two
cities is their Euclidean distance rounded to an integer.

The model reports the length of the shortest route.
"""
import math

import pulp


def build(instance):
    locations = instance["locations"]  # [x, y] of every city
    n = len(locations)

    # distance[i][j] = Euclidean distance between cities i and j, rounded to an integer
    # (computed as in the reference)
    distance = [[int(round(math.hypot(locations[i][0] - locations[j][0],
                                      locations[i][1] - locations[j][1])))
                 for j in range(n)] for i in range(n)]

    problem = pulp.LpProblem("tsp", pulp.LpMinimize)

    # next_to[i][j] = 1 if the route goes from city i straight to city j
    pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
    next_to = {(i, j): pulp.LpVariable(f"next_{i}_{j}", cat="Binary") for i, j in pairs}

    # every city is left once and entered once
    for i in range(n):
        problem += pulp.lpSum(next_to[(i, j)] for j in range(n) if j != i) == 1
        problem += pulp.lpSum(next_to[(j, i)] for j in range(n) if j != i) == 1

    # The legs must form one circuit through all cities, not several smaller ones. City 0
    # sends n - 1 units of "flow" along the legs of the route; every other city keeps one unit
    # and passes the rest on. Cities that form a circuit apart from city 0 could not receive
    # flow, so there is none. flow[(i, j)] is the flow on the leg from i to j; no flow enters
    # city 0.
    flow = {(i, j): pulp.LpVariable(f"flow_{i}_{j}", 0, n - 1 if i == 0 else n - 2)
            for i, j in pairs if j != 0}
    problem += pulp.lpSum(flow[(0, j)] for j in range(1, n)) == n - 1
    for i in range(1, n):
        problem += (pulp.lpSum(flow[(j, i)] for j in range(n) if j != i)
                    - pulp.lpSum(flow[(i, j)] for j in range(1, n) if j != i)) == 1
    for (i, j), f in flow.items():
        # flow only travels along legs of the route, at most n - 1 units from city 0 and
        # n - 2 units from the other cities (city i has kept one), and at least the unit that
        # city j keeps
        problem += f <= (n - 1 if i == 0 else n - 2) * next_to[(i, j)]
        problem += f >= next_to[(i, j)]

    # With three or more cities the route does not go back and forth between two cities.
    # (Already excluded by the flow; stated because it tightens the relaxation.)
    if n > 2:
        for i in range(n):
            for j in range(i + 1, n):
                problem += next_to[(i, j)] + next_to[(j, i)] <= 1

    # Symmetry: distances are symmetric, so a route and the same route driven backwards have the
    # same length. Only the routes in which the city after city 0 has a smaller index than the
    # city before it are kept. This removes one of every two mirrored routes and leaves the
    # shortest length, which is all that is reported, unchanged.
    if n > 2:
        problem += (pulp.lpSum(j * next_to[(0, j)] for j in range(1, n))
                    <= pulp.lpSum(j * next_to[(j, 0)] for j in range(1, n)))

    # travel_distance = total length of the route; the most it can be is each city's longest leg
    longest = sum(max(distance[i][j] for j in range(n) if j != i) for i in range(n))
    travel_distance = pulp.LpVariable("travel_distance", 0, longest, cat="Integer")
    problem += travel_distance == pulp.lpSum(distance[i][j] * next_to[(i, j)] for i, j in pairs)

    # minimise the length of the route
    problem += travel_distance

    return problem, {"travel_distance": travel_distance}

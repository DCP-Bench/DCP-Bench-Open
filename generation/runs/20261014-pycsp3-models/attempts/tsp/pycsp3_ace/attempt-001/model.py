import builtins
from math import sqrt

from pycsp3 import *

# Travelling salesman: visit every city exactly once and return to the start, with the
# shortest total distance. The distance between two cities is the Euclidean distance rounded to an integer.
locations = data.locations
n = len(locations)

# dist[i][j] is the rounded Euclidean distance between city i and city j
dist = [[round(sqrt((locations[i][0] - locations[j][0]) ** 2 + (locations[i][1] - locations[j][1]) ** 2))
         for j in range(n)] for i in range(n)]
max_dist = builtins.max(builtins.max(row) for row in dist)

# every city is left by one leg, and each leg is at least the shortest leg leaving that city
shortest_leg = [builtins.min(dist[i][j] for j in range(n) if j != i) for i in range(n)]

# nearest-neighbour tour: its length is an upper bound on the optimal travel distance
visited = [False] * n
tour_length, here = 0, 0
visited[0] = True
for _ in range(n - 1):
    nxt = builtins.min((j for j in range(n) if not visited[j]), key=lambda j: dist[here][j])
    tour_length += dist[here][nxt]
    visited[nxt] = True
    here = nxt
tour_length += dist[here][0]

# succ[i] is the city visited right after city i
succ = VarArray(size=n, dom=range(n))

# leg[i] is the distance of the leg leaving city i
leg = VarArray(size=n, dom=range(0, max_dist + 1))

# travel_distance is the total length of the tour, between the sum of the shortest legs and the heuristic tour
travel_distance = Var(dom=range(builtins.sum(shortest_leg), tour_length + 1))

satisfy(
    # the successors form one tour that visits every city once
    Circuit(succ),
    # the leg from each city has the distance to the city that follows it
    [Table(scope=[succ[i], leg[i]], supports=[(j, dist[i][j]) for j in range(n) if j != i])
     for i in range(n)],
    # the travel distance is the sum of the legs
    travel_distance == Sum(leg),
    # each leg is at least the shortest leg leaving its city
    [leg[i] >= shortest_leg[i] for i in range(n)],
)

# minimise the travel distance
minimize(travel_distance)

The travelling salesman problem: a list of cities and the distances between each pair -> dist[i][j] = round(Euclidean distance) computed from locations (instance field), n = number of cities
what is the shortest possible route that visits each city exactly once and returns to the origin city -> succ[i] = next city after i (0-based), m.circuit(succ).post()
visits each city exactly once and returns to the origin city -> circuit (one cycle through all cities, no sub-tours)
the optimal travel distance -> cost[i] = element(dist[i], succ[i]) per city, total = sum(cost), MINIMIZE total, output travel_distance

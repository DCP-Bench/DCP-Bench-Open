Given a list of cities and the distances between each pair of cities, find the shortest possible route -> circuit(*this, IntArgs(cost), succ, total) [succ[i] = next city; cost is the n x n row-major matrix built from the instance locations]
visits each city exactly once and returns to the origin city -> circuit(*this, IntArgs(cost), succ, total) [a single Hamiltonian cycle, same post as above]
distance is the Euclidean distance between the points rounded to an integer -> cost[i][j] = lround(sqrt(dx*dx + dy*dy)) computed in C++ from the locations (data transform, no global)
print the optimal travel distance -> total, the IntVar cost argument of circuit, exposed as output travel_distance
branching -> branch(*this, succ, INT_VAR_SIZE_MIN(), INT_VAL_MIN()) on the successors; total is then fixed by propagation
objective -> minimize(total) [shortest tour]

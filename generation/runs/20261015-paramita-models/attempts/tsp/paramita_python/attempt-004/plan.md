A route that visits each city exactly once -> successor Bool succ[i][j] with sum == 1 per row (leaves city i once) and sum == 1 per column (enters city j once)
and returns to the origin city -> the origin 0 is the start: its position is 0 and the route closes back into 0 (succ[i][0] only from the last position)
The route is one closed loop, no shorter loops -> unary position u_i >= k (ge[i][k], k = 1..n-1), succ[i][j] with j != 0 -> u_j >= u_i + 1 as clauses on ge; two-city loops excluded by ~succ[i][j] | ~succ[j][i]
The distance is the Euclidean distance rounded to an integer -> d[i][j] = round(hypot(dx, dy)) from the instance locations
Print the optimal travel distance (travel_distance) -> output = sum of d[i][j] * succ[i][j] as row sums
Objective: minimize travel_distance (PB sum over the successor Bools)

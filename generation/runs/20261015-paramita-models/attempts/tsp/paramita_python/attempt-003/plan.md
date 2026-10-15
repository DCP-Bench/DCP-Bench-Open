A route that visits each city exactly once and returns to the origin city -> successor Bool succ[i][j], exactly one next city and one previous city per city (sum == 1)
The route must be one closed loop through all cities (no shorter loops) -> unary order u_i for each city (ge[i][k] = u_i >= k), origin city 0 fixed at u_0 = 0; succ[i][j] -> u_j >= u_i + 1 as implications on the unary Bools; succ[i][0] -> u_i = n-1
The distance is the Euclidean distance between the points rounded to an integer -> d[i][j] = round(sqrt(dx^2+dy^2)) from the instance locations
Print the optimal travel distance (travel_distance) -> output = sum of d[i][j] * succ[i][j], as sums of row sums
Objective: minimize travel_distance

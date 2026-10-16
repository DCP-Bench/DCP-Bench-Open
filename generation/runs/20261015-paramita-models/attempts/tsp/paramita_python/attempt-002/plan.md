A route that visits each city exactly once and returns to the origin city -> one-hot position pos[i][k] per city (city 0 fixed at position 0), each city one position and each position one city (sum == 1)
Each city has exactly one next city and one previous city -> successor Bool succ[i][j], sum == 1 per row and column
Successor follows the positions (subtour-free) -> pos[i][k] & pos[j][k+1 mod n] <-> succ[i][j] (both directions as clauses, so the successor Bools are fixed by the positions)
The distance is the Euclidean distance between the points rounded to an integer -> d[i][j] = round(sqrt(dx^2+dy^2)) from the instance locations
Print the optimal travel distance (travel_distance) -> output = sum of d[i][j] * succ[i][j], as sums of row sums
Objective: minimize travel_distance

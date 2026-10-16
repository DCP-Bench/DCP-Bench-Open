A route that visits each city exactly once and returns to the origin city -> one-hot position pos[i][k] per city (city 0 fixed at position 0), each city one position and each position one city (sum == 1), successor Bool e[i][j] with exactly one outgoing and one incoming edge per city (sum == 1), and e[i][j] & pos[i][k] -> pos[j][k+1 mod n] (PB/clauses, subtour-free because positions form one cycle)
The distance is the Euclidean distance between the points rounded to an integer -> d[i][j] = round(sqrt(dx^2+dy^2)) computed from the instance locations
Print the optimal travel distance (travel_distance) -> output travel_distance = sum of d[i][j] * e[i][j]
Objective: minimize travel_distance (PB sum over the edge Bools, grouped as sums of row sums)

"""Solve the given 12-city Euclidean TSP with Google OR-Tools (CP-SAT)

The model follows the classical Miller–Tucker–Zemlin (MTZ) formulation with
explicit directed arc variables.  The only value reported is the optimal tour
length (travel_distance).
"""

from ortools.sat.python import cp_model
import math
import json

# -----------------------------------------------------------------------------
# 1. Immutable input data (exact copy of the specification)
# -----------------------------------------------------------------------------
locations = [
    (288, 149), (288, 129), (270, 133), (256, 141), (256, 163), (246, 157),
    (236, 169), (228, 169), (228, 148), (220, 164), (212, 172), (204, 159)
]

# -----------------------------------------------------------------------------
# 2. Derived data – integer distance matrix (scaled to keep CP-SAT integral)
# -----------------------------------------------------------------------------
N = len(locations)
SCALE = 1000  # scale factor to convert floating point distances to integers

dist = [[0] * N for _ in range(N)]
max_single = 0
for i in range(N):
    x_i, y_i = locations[i]
    for j in range(N):
        if i == j:
            continue
        x_j, y_j = locations[j]
        d = math.hypot(x_i - x_j, y_i - y_j)
        d_int = int(round(d * SCALE))  # integer distance
        dist[i][j] = d_int
        if d_int > max_single:
            max_single = d_int

# Tight upper bound for travel_distance: n * max_single_distance
MAX_TOUR = N * max_single

# -----------------------------------------------------------------------------
# 3. CP-SAT model (MTZ formulation)
# -----------------------------------------------------------------------------
model = cp_model.CpModel()

# 3.1 Directed arc selection variables x[i][j]  (i ≠ j)
x = [[None] * N for _ in range(N)]
for i in range(N):
    for j in range(N):
        if i == j:
            continue
        x[i][j] = model.NewBoolVar(f"x_{i}_{j}")

# 3.2 Degree constraints: exactly one outgoing and one incoming arc per node
for i in range(N):
    # Out-degree = 1
    model.Add(sum(x[i][j] for j in range(N) if j != i) == 1)
    # In-degree  = 1
    model.Add(sum(x[j][i] for j in range(N) if j != i) == 1)

# 3.3 MTZ sub-tour elimination variables u_i (only for nodes 1..N-1, u_0 = 0)
u = {0: model.NewIntVar(0, 0, "u_0")}
for i in range(1, N):
    u[i] = model.NewIntVar(1, N - 1, f"u_{i}")

# MTZ constraints:  u_i - u_j + N * x[i][j] ≤ N-1   for all i ≠ j, i,j ≥ 1
for i in range(1, N):
    for j in range(1, N):
        if i == j:
            continue
        model.Add(u[i] - u[j] + N * x[i][j] <= N - 1)

# 3.4 Objective variable: travel_distance (integer, scaled)
travel_distance = model.NewIntVar(0, MAX_TOUR, "travel_distance")
model.Add(travel_distance == sum(dist[i][j] * x[i][j] for i in range(N) for j in range(N) if i != j))

# Minimise the total travel distance
model.Minimize(travel_distance)

# -----------------------------------------------------------------------------
# 4. Solver configuration and execution
# -----------------------------------------------------------------------------
solver = cp_model.CpSolver()
# Small instance – let the solver prove optimality without a hard time-limit
solver.parameters.num_search_workers = 8  # use all available cores if possible

status = solver.Solve(model)

# -----------------------------------------------------------------------------
# 5. Extract and print the solution in the required JSON format
# -----------------------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    distance_value = solver.Value(travel_distance) / SCALE  # convert back to float
    print(json.dumps({"travel_distance": distance_value}))
else:
    # According to the specification the output must still be valid JSON
    print(json.dumps({"travel_distance": None}))
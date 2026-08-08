from ortools.sat.python import cp_model
import json
import math

# Input data
locations = [
    (288, 149), (288, 129), (270, 133), (256, 141), (256, 163), (246, 157),
    (236, 169), (228, 169), (228, 148), (220, 164), (212, 172), (204, 159)
]

num_cities = len(locations)

# Calculate Euclidean distances between cities, rounded to integers
distances = {}
for i in range(num_cities):
    for j in range(num_cities):
        if i != j:
            dx = locations[i][0] - locations[j][0]
            dy = locations[i][1] - locations[j][1]
            distances[(i, j)] = int(round(math.sqrt(dx * dx + dy * dy)))
        else:
            distances[(i, j)] = 0

# Model definition
model = cp_model.CpModel()

# Decision variables:
# next_city[i] = the city visited immediately after city i
next_city = [model.NewIntVar(0, num_cities - 1, f'next_city_{i}') for i in range(num_cities)]

# All cities must be visited exactly once, so next_city forms a permutation with no fixed points
# We will enforce that next_city forms a single Hamiltonian circuit

# Add circuit constraint using arcs
# The circuit constraint requires a list of arcs (tail, head, literal)
# We create literals for all possible arcs and link them to next_city variables

# Create literals for arcs
arc_literals = {}
for i in range(num_cities):
    for j in range(num_cities):
        if i != j:
            arc_literals[(i, j)] = model.NewBoolVar(f'arc_{i}_{j}')
        else:
            arc_literals[(i, j)] = None  # no self loops

# Link next_city variables to arc literals
for i in range(num_cities):
    # next_city[i] == j <=> arc_literals[(i,j)] == True
    # We enforce exactly one arc out of city i
    model.AddAllowedAssignments([next_city[i]] + [arc_literals[(i, j)] for j in range(num_cities) if j != i],
                                [(j,) + tuple(1 if k == j else 0 for k in range(num_cities) if k != i) for j in range(num_cities) if j != i])

# Each city has exactly one incoming arc
for j in range(num_cities):
    incoming = [arc_literals[(i, j)] for i in range(num_cities) if i != j]
    model.AddExactlyOne(incoming)

# Each city has exactly one outgoing arc
for i in range(num_cities):
    outgoing = [arc_literals[(i, j)] for j in range(num_cities) if j != i]
    model.AddExactlyOne(outgoing)

# Add circuit constraint
arcs = []
for i in range(num_cities):
    for j in range(num_cities):
        if i != j:
            arcs.append(cp_model.Arc(i, j, arc_literals[(i, j)]))
model.AddCircuit(arcs)

# Objective: minimize total travel distance
total_distance = model.NewIntVar(0, 1000000, 'total_distance')
model.Add(total_distance == sum(distances[(i, j)] * arc_literals[(i, j)] for i in range(num_cities) for j in range(num_cities) if i != j))
model.Minimize(total_distance)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    travel_distance = solver.Value(total_distance)
    solution = {
        'travel_distance': travel_distance
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
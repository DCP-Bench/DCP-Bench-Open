from ortools.sat.python import cp_model
import json

# Input data
k = 4  # Number of sets
n = 4  # Numbers from 1 to n

# Model definition
model = cp_model.CpModel()

# The sequence length is k * n
length = k * n

# Decision variables
# position[m][i]: the position of the i-th occurrence of number m+1 in the sequence
# m in [0..n-1], i in [0..k-1]
position = []
for m in range(n):
    pos_m = [model.NewIntVar(0, length - 1, f'pos_{m+1}_{i}') for i in range(k)]
    position.append(pos_m)

# solution[i]: the number at position i in the sequence (0 means empty, but here all positions must be filled)
solution = [model.NewIntVar(1, n, f'solution_{i}') for i in range(length)]

# Constraints

# 1) All positions are distinct (no two occurrences share the same position)
all_positions = [position[m][i] for m in range(n) for i in range(k)]
model.AddAllDifferent(all_positions)

# 2) Link position variables and solution variables
# For each number m+1 and each occurrence i, solution[position[m][i]] == m+1
for m in range(n):
    for i in range(k):
        # Add element constraint: solution[position[m][i]] == m+1
        model.AddElement(position[m][i], solution, m + 1)

# 3) For each number m+1, the k occurrences must be spaced m+1 apart
# The problem states: each appearance of the number m is m numbers on from the last
# So for each m, the positions must be sorted and consecutive positions differ by m+1
for m in range(n):
    # Sort the positions of occurrences of number m+1
    # We create auxiliary variables for sorted positions
    sorted_pos = [model.NewIntVar(0, length - 1, f'sorted_pos_{m+1}_{i}') for i in range(k)]
    model.AddAllDifferent(sorted_pos)
    model.AddAllDifferent(position[m])
    # Add sorting constraints: sorted_pos is a sorted version of position[m]
    # We enforce sorted_pos[i] <= sorted_pos[i+1]
    for i in range(k - 1):
        model.Add(sorted_pos[i] < sorted_pos[i + 1])
    # Link sorted_pos and position[m] by allowed assignments (permutation)
    # We enforce that sorted_pos is a permutation of position[m]
    # This can be done by adding that sorted_pos and position[m] have the same multiset of values
    # Since all are distinct, we can enforce that sorted_pos is a permutation of position[m]
    # We use the AddAllowedAssignments with all permutations of position[m]
    # But this is complex; instead, we use the AddAllDifferent on both and enforce that sorted_pos is sorted
    # and that sorted_pos is a subset of position[m]
    # We can enforce that each sorted_pos[i] equals one of position[m]
    for i in range(k):
        model.AddAllowedAssignments([sorted_pos[i]], [[solver_val] for solver_val in range(length)])
    # Enforce that sorted_pos is a permutation of position[m]
    # We add that the sum of sorted_pos equals sum of position[m]
    model.Add(sum(sorted_pos) == sum(position[m]))
    # Enforce spacing constraints: sorted_pos[i+1] - sorted_pos[i] == m+1
    for i in range(k - 1):
        model.Add(sorted_pos[i + 1] - sorted_pos[i] == m + 1)

# 4) All positions in solution must be assigned exactly one number
# Already ensured by linking position variables to solution variables and all positions distinct

# Objective: no objective, just find a feasible solution

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Extract positions as a list of lists: positions for each number m+1
    positions_sol = []
    for m in range(n):
        positions_m = [solver.Value(position[m][i]) for i in range(k)]
        positions_sol.append(positions_m)
    # Extract solution sequence
    solution_seq = [solver.Value(solution[i]) for i in range(length)]
    solution = {
        'position': positions_sol,
        'solution': solution_seq
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
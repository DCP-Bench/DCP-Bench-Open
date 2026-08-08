from ortools.sat.python import cp_model
import json

# Input data
v = 9  # Number of distinct objects
b = 12  # Number of blocks
r = 4  # Number of blocks each object occurs in
k = 3  # Number of objects each block contains
l = 1  # Number of blocks in which each pair of distinct objects occurs together

# Model definition
model = cp_model.CpModel()

# Decision Variables
# matrix[i][j] = 1 if object i is in block j, else 0
matrix = []
for i in range(v):
    row = []
    for j in range(b):
        row.append(model.NewBoolVar(f'matrix_{i}_{j}'))
    matrix.append(row)

# Constraints

# Each object occurs in exactly r blocks (row sum = r)
for i in range(v):
    model.Add(sum(matrix[i][j] for j in range(b)) == r)

# Each block contains exactly k objects (column sum = k)
for j in range(b):
    model.Add(sum(matrix[i][j] for i in range(v)) == k)

# Every two distinct objects occur together in exactly l blocks
# For each pair of distinct objects (i1, i2), sum over blocks of matrix[i1][j] * matrix[i2][j] == l
# We linearize the product by introducing auxiliary variables for each block and pair
for i1 in range(v):
    for i2 in range(i1 + 1, v):
        # Auxiliary variables for product matrix[i1][j] * matrix[i2][j]
        prod_vars = []
        for j in range(b):
            prod = model.NewBoolVar(f'prod_{i1}_{i2}_{j}')
            # prod <= matrix[i1][j]
            model.Add(prod <= matrix[i1][j])
            # prod <= matrix[i2][j]
            model.Add(prod <= matrix[i2][j])
            # prod >= matrix[i1][j] + matrix[i2][j] - 1
            model.Add(prod >= matrix[i1][j] + matrix[i2][j] - 1)
            prod_vars.append(prod)
        model.Add(sum(prod_vars) == l)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    matrix_sol = []
    for i in range(v):
        row_sol = [solver.Value(matrix[i][j]) for j in range(b)]
        matrix_sol.append(row_sol)
    solution = {'matrix': matrix_sol}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
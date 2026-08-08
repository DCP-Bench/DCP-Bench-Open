from ortools.sat.python import cp_model
import json

# Input data
n = 10  # Length of the binary sequence

# Model definition
model = cp_model.CpModel()

# Decision Variables
# Represent each bit as an integer variable taking values -1 or 1
# Since OR-tools does not support negative domain directly, we use 0/1 and map to -1/+1
bits = [model.NewIntVar(0, 1, f'bit_{i}') for i in range(n)]

# Helper variables to represent S_i as -1 or +1
# S_i = 2 * bits[i] - 1
# We will use this expression directly in constraints and objective

# Compute autocorrelations C_k for k=1 to n-1
# C_k = sum_{i=0}^{n-k-1} S_i * S_{i+k} (non-periodic)
# S_i = 2*bits[i] - 1
# So S_i * S_j = (2*bits[i]-1)*(2*bits[j]-1) = 4*bits[i]*bits[j] - 2*bits[i] - 2*bits[j] + 1

# We will create integer variables for each C_k
C = []
for k in range(1, n):
    # Calculate terms for C_k
    terms = []
    for i in range(n - k):
        # bits[i] and bits[i+k] are 0/1 variables
        # We need to model product bits[i]*bits[i+k]
        # Create an auxiliary variable for product bits[i]*bits[i+k]
        prod = model.NewIntVar(0, 1, f'prod_{i}_{i+k}')
        model.AddMultiplicationEquality(prod, [bits[i], bits[i + k]])
        # Expression for S_i * S_{i+k} = 4*prod - 2*bits[i] - 2*bits[i+k] + 1
        # We'll sum these expressions
        terms.append((prod, bits[i], bits[i + k]))
    # Now create an integer variable for C_k
    # The range of C_k can be from -(n-k) to (n-k)
    Ck = model.NewIntVar(-(n - k), n - k, f'C_{k}')
    # We will create an expression for Ck as sum of S_i * S_{i+k}
    # Since OR-tools does not support direct sum of expressions with variables multiplied by constants,
    # we create an intermediate variable for sum of all terms
    # sum_{i} (4*prod - 2*bits[i] - 2*bits[i+k] + 1) = 4*sum(prod) - 2*sum(bits[i]) - 2*sum(bits[i+k]) + (n-k)
    sum_prod = model.NewIntVar(0, n - k, f'sum_prod_{k}')
    model.Add(sum_prod == sum(prod for (prod, _, _) in terms))
    sum_bits_i = model.NewIntVar(0, n - k, f'sum_bits_i_{k}')
    model.Add(sum_bits_i == sum(bi for (_, bi, _) in terms))
    sum_bits_j = model.NewIntVar(0, n - k, f'sum_bits_j_{k}')
    model.Add(sum_bits_j == sum(bj for (_, _, bj) in terms))
    # Define Ck = 4*sum_prod - 2*sum_bits_i - 2*sum_bits_j + (n-k)
    # We use a linear expression for Ck
    model.Add(Ck == 4 * sum_prod - 2 * sum_bits_i - 2 * sum_bits_j + (n - k))
    C.append(Ck)

# Objective: minimize sum of squares of C_k for k=1 to n-1
# We need to model squares of C_k
# Since C_k ranges from -(n-k) to (n-k), max abs value is n-1
# We create auxiliary variables for squares
C_squares = []
for k in range(n - 1):
    sq = model.NewIntVar(0, (n - 1) * (n - 1), f'C_{k+1}_square')
    model.AddMultiplicationEquality(sq, [C[k], C[k]])
    C_squares.append(sq)

model.Minimize(sum(C_squares))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Extract sequence as +1/-1
    sequence = [2 * solver.Value(bits[i]) - 1 for i in range(n)]
    E = solver.ObjectiveValue()
    solution = {
        'sequence': sequence,
        'E': int(E)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
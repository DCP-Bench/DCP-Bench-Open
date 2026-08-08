from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Given fixed values
A_val = 16
B_val = 2
F_val = 8
G_val = 14

# Variables: C, D, E, H, I, K
# Each number is an integer between 1 and 99 (two figures max)
C = model.NewIntVar(1, 99, 'C')
D = model.NewIntVar(1, 99, 'D')
E = model.NewIntVar(1, 99, 'E')
H = model.NewIntVar(1, 99, 'H')
I = model.NewIntVar(1, 99, 'I')
K = model.NewIntVar(1, 99, 'K')

# All numbers must be different
all_vars = [A_val, B_val, C, D, E, F_val, G_val, H, I, K]
# Since A, B, F, G are fixed, we only add constraints for distinctness among variables and fixed values
model.AddAllDifferent([C, D, E, H, I, K, B_val, A_val, F_val, G_val])

# Define a helper function to add the sum of squares equality constraint
def sum_squares_equal(x1, x2, y1, y2):
    # x1^2 + x2^2 == y1^2 + y2^2
    # Since some are fixed values, handle accordingly
    def square(val):
        if isinstance(val, int):
            return val * val
        else:
            return model.NewIntVar(0, 99*99, f'sq_{val.Name()}')

    # For variables, create auxiliary variables for squares
    def get_square_var(val):
        if isinstance(val, int):
            return val * val
        else:
            sq = model.NewIntVar(0, 99*99, f'sq_{val.Name()}')
            model.AddMultiplicationEquality(sq, [val, val])
            return sq

    x1_sq = get_square_var(x1)
    x2_sq = get_square_var(x2)
    y1_sq = get_square_var(y1)
    y2_sq = get_square_var(y2)

    model.Add(x1_sq + x2_sq == y1_sq + y2_sq)

# The circle is: A, B, C, D, E, F, G, H, I, K
# The pairs of adjacent squares and their opposite pairs are:
# (A,B) opposite (F,E)
# (B,C) opposite (G,H)
# (C,D) opposite (H,I)
# (D,E) opposite (I,K)
# (E,F) opposite (K,A)
# (F,G) opposite (A,B) - but this is already covered as (A,B) opposite (F,E)
# The problem states "and so on, with any two adjoining squares in the circle."

# We will consider all adjacent pairs and their opposite pairs:
# The circle indices: 0:A,1:B,2:C,3:D,4:E,5:F,6:G,7:H,8:I,9:K
# Adjacent pairs and opposite pairs:
# (A,B) (F,E)
sum_squares_equal(A_val, B_val, F_val, E)
# (B,C) (G,H)
sum_squares_equal(B_val, C, G_val, H)
# (C,D) (H,I)
sum_squares_equal(C, D, H, I)
# (D,E) (I,K)
sum_squares_equal(D, E, I, K)
# (E,F) (K,A)
sum_squares_equal(E, F_val, K, A_val)
# (F,G) (A,B) - already covered as (A,B) opposite (F,E), so skip
# (G,H) (B,C) - already covered
# (H,I) (C,D) - already covered
# (I,K) (D,E) - already covered
# (K,A) (E,F) - already covered

# So only the five constraints above are needed.

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'A': A_val,
        'B': B_val,
        'C': solver.Value(C),
        'D': solver.Value(D),
        'E': solver.Value(E),
        'F': F_val,
        'G': G_val,
        'H': solver.Value(H),
        'I': solver.Value(I),
        'K': solver.Value(K)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
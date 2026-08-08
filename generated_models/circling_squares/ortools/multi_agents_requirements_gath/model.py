import json
from ortools.sat.python import cp_model

# ----------------------------
# Model creation
# ----------------------------
model = cp_model.CpModel()

# Constant upper/lower bounds (1..99, two–digit maximum)
LOW, UP = 1, 99

# Squares lookup table 0..99 (index i holds i*i)
squares = [i * i for i in range(UP + 1)]  # length 100

# Helper to create a value variable and its square variable that is linked via an element constraint
def create_val_and_square(name: str):
    v = model.NewIntVar(LOW, UP, name)
    sv = model.NewIntVar(LOW * LOW, UP * UP, f"sq_{name}")
    model.AddElement(v, squares, sv)
    return v, sv

# Decision variables (value + square counterpart)
A, sq_A = model.NewIntVar(16, 16, "A"), model.NewIntVar(16 * 16, 16 * 16, "sq_A")
B, sq_B = model.NewIntVar(2, 2, "B"), model.NewIntVar(2 * 2, 2 * 2, "sq_B")
F, sq_F = model.NewIntVar(8, 8, "F"), model.NewIntVar(8 * 8, 8 * 8, "sq_F")
G, sq_G = model.NewIntVar(14, 14, "G"), model.NewIntVar(14 * 14, 14 * 14, "sq_G")
# Link the fixed variables to their squares
model.Add(sq_A == 16 * 16)
model.Add(sq_B == 2 * 2)
model.Add(sq_F == 8 * 8)
model.Add(sq_G == 14 * 14)

C, sq_C = create_val_and_square("C")
D, sq_D = create_val_and_square("D")
E, sq_E = create_val_and_square("E")
H, sq_H = create_val_and_square("H")
I, sq_I = create_val_and_square("I")
K, sq_K = create_val_and_square("K")

# All-different on the ten value variables
values = [A, B, C, D, E, F, G, H, I, K]
model.AddAllDifferent(values)

# ----------------------------
# Square–sum equality constraints for opposite adjacent pairs
# ----------------------------
# 1) A^2 + B^2 = F^2 + G^2  (already true for fixed constants but added for completeness)
model.Add(sq_A + sq_B == sq_F + sq_G)
# 2) B^2 + C^2 = G^2 + H^2
model.Add(sq_B + sq_C == sq_G + sq_H)
# 3) C^2 + D^2 = H^2 + I^2
model.Add(sq_C + sq_D == sq_H + sq_I)
# 4) D^2 + E^2 = I^2 + K^2
model.Add(sq_D + sq_E == sq_I + sq_K)
# 5) E^2 + F^2 = K^2 + A^2
model.Add(sq_E + sq_F == sq_K + sq_A)

# ----------------------------
# Solve model
# ----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10  # reasonable time limit
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError("No solution found within the time limit.")

# Extract solution into required JSON order
result = {
    'H': solver.Value(H),
    'D': solver.Value(D),
    'K': solver.Value(K),
    'G': solver.Value(G),
    'E': solver.Value(E),
    'C': solver.Value(C),
    'I': solver.Value(I),
    'F': solver.Value(F),
    'A': solver.Value(A),
    'B': solver.Value(B),
}

print(json.dumps(result))
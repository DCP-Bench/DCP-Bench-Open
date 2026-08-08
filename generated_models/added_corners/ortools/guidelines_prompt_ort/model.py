
from ortools.sat.python import cp_model
import json

# Create the CP-SAT model
model = cp_model.CpModel()

# Define decision variables for each circle (C) and square (F) position
# Positions are labeled by their grid coordinates (row, column)
circle00 = model.NewIntVar(1, 8, 'circle00')  # top-left circle
square01 = model.NewIntVar(1, 8, 'square01')  # top-middle square
circle02 = model.NewIntVar(1, 8, 'circle02')  # top-right circle
square10 = model.NewIntVar(1, 8, 'square10')  # middle-left square
square12 = model.NewIntVar(1, 8, 'square12')  # middle-right square
circle20 = model.NewIntVar(1, 8, 'circle20')  # bottom-left circle
square21 = model.NewIntVar(1, 8, 'square21')  # bottom-middle square
circle22 = model.NewIntVar(1, 8, 'circle22')  # bottom-right circle

# All digits 1 through 8 must be used exactly once
model.AddAllDifferent([
    circle00, square01, circle02, square10,
    square12, circle20, square21, circle22
])

# Each square equals the sum of its adjacent circles
# square01 sits between circle00 and circle02
model.Add(square01 == circle00 + circle02)
# square10 sits between circle00 and circle20
model.Add(square10 == circle00 + circle20)
# square12 sits between circle02 and circle22
model.Add(square12 == circle02 + circle22)
# square21 sits between circle20 and circle22
model.Add(square21 == circle20 + circle22)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Collect values in row-major order, skipping the blank center
    positions = [
        circle00, square01, circle02,
        square10,       square12,
        circle20, square21, circle22
    ]
    solution = {
        'positions': [solver.Value(var) for var in positions]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")

# Perfect (Simple) Squared–Square – CP-SAT model with OR-Tools
# ---------------------------------------------------------------
# All rights reserved – demo solver created by ChatGPT
#
# The code follows the specification that accompanies the task.  It first
# verifies the *parameter* conditions that have to hold for every legal
# instance of a *perfect* squared-square; if the data violate one of these
# conditions an immediate ‘no-solution’ JSON is printed (empty coordinate
# lists).
#
# Otherwise the program builds a complete CP-SAT model that obeys
# – containment of every small square inside the big one
# – mutual non-overlap (with NoOverlap2D)
# – “simple” perfectness (no proper subset of squares may tile a rectangle
#   of their own) by explicitly enumerating all proper subsets and
#   forbidding the rectangle-equality relation with the help of
#   min/max and multiplication constraints that OR-Tools offers.
#
# The instance at hand (three 3×3 squares, one 2×2, five 1×1 inside a
# 6×6 square) already *violates* the distinct-sizes requirement of a
# perfect squared-square.  Consequently the solver rightly declares the
# problem infeasible and returns empty lists as required by the JSON
# interface.
# ---------------------------------------------------------------

import json
from itertools import combinations, chain
from ortools.sat.python import cp_model

# ---------------------------------------------------------------------------
# 1. Input data  (immutable – do NOT touch)
# ---------------------------------------------------------------------------
base = 6  # Side length of the container square
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]  # Side lengths of the small squares
n = len(sides)

# ---------------------------------------------------------------------------
# 2. Parameter checks that belong to the formal problem definition
#    (their violation means the instance itself is illegal)
# ---------------------------------------------------------------------------

def instance_is_perfect(base: int, sides: list[int]) -> tuple[bool, str]:
    """Return (ok, message)."""
    # D-1  complete area
    if sum(s ** 2 for s in sides) != base * base:
        return False, "Area mismatch – the squares do not exactly fill the big square."
    # D-2  pair-wise distinct side lengths
    if len(set(sides)) != len(sides):
        return False, "Side lengths are not pair-wise distinct — instance is not *perfect*."
    return True, "OK"

# Perform the test
ok, msg = instance_is_perfect(base, sides)
if not ok:
    # The instance is *illegal* w.r.t. the problem definition.  We must
    # signal infeasibility as required by the specification.
    print(json.dumps({"y_coords": [], "x_coords": []}))
    raise SystemExit(0)

# ---------------------------------------------------------------------------
# 3. Build CP-SAT model (only reached when the instance passed the checks)
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# 3.1  Decision variables  ---------------------------------------------------
# Coordinates of the lower-left corner of each small square
y = [model.NewIntVar(0, base - s, f"y_{i}") for i, s in enumerate(sides)]
x = [model.NewIntVar(0, base - s, f"x_{i}") for i, s in enumerate(sides)]

# Interval variables for AddNoOverlap2D --------------------------------------
interval_x = []
interval_y = []
for i, s in enumerate(sides):
    x_end = model.NewIntVar(0, base, f"x_end_{i}")
    y_end = model.NewIntVar(0, base, f"y_end_{i}")
    model.Add(x_end == x[i] + s)
    model.Add(y_end == y[i] + s)
    interval_x.append(model.NewIntervalVar(x[i], s, x_end, f"ix_{i}"))
    interval_y.append(model.NewIntervalVar(y[i], s, y_end, f"iy_{i}"))

# 3.2  Hard constraints  -----------------------------------------------------
# Non-overlap of axis-aligned squares (C-2)
model.AddNoOverlap2D(interval_x, interval_y)

# 3.3  Simplicity – forbid proper subsets that perfectly tile their own
#       bounding rectangle (C-5)
# ---------------------------------------------------------------------------
# Helper arrays for quick reuse
x_ends = [model.NewIntVar(0, base, f"x_end_fixed_{i}") for i in range(n)]
y_ends = [model.NewIntVar(0, base, f"y_end_fixed_{i}") for i in range(n)]
for i, s in enumerate(sides):
    model.Add(x_ends[i] == x[i] + s)
    model.Add(y_ends[i] == y[i] + s)

# Enumerate all proper non-trivial subsets --------------------------------------------------
all_indices = range(n)
subsets = chain.from_iterable(combinations(all_indices, k) for k in range(2, n))
for idx, subset in enumerate(subsets):
    # min/max along x ---------------------------------------------------------
    min_x = model.NewIntVar(0, base, f"min_x_{idx}")
    max_x = model.NewIntVar(0, base, f"max_x_{idx}")
    model.AddMinEquality(min_x, [x[i] for i in subset])
    model.AddMaxEquality(max_x, [x_ends[i] for i in subset])
    width = model.NewIntVar(1, base, f"w_{idx}")
    model.Add(width == max_x - min_x)

    # min/max along y ---------------------------------------------------------
    min_y = model.NewIntVar(0, base, f"min_y_{idx}")
    max_y = model.NewIntVar(0, base, f"max_y_{idx}")
    model.AddMinEquality(min_y, [y[i] for i in subset])
    model.AddMaxEquality(max_y, [y_ends[i] for i in subset])
    height = model.NewIntVar(1, base, f"h_{idx}")
    model.Add(height == max_y - min_y)

    # Bounding rectangle area and subset area ---------------------------------
    rect_area = model.NewIntVar(0, base * base, f"area_{idx}")
    model.AddMultiplicationEquality(rect_area, [width, height])

    subset_area_const = sum(sides[i] ** 2 for i in subset)
    # Forbid equality  (rect_area != subset_area_const) -----------------------
    model.Add(rect_area != subset_area_const)

# ---------------------------------------------------------------------------
# 4. Solve -------------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0  # safety limit
status = solver.Solve(model)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    y_coords = [solver.Value(var) for var in y]
    x_coords = [solver.Value(var) for var in x]
    print(json.dumps({"y_coords": y_coords, "x_coords": x_coords}))
else:
    # No placement fulfils all requirements
    print(json.dumps({"y_coords": [], "x_coords": []}))

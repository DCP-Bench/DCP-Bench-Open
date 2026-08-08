"""Supply-vessel single-layer deck-loading – feasibility model
================================================================
This program tests whether a given list of rectangular containers can be
placed on a rectangular ship deck subject to a set of hard constraints (see
problem statement).  All data are embedded exactly as supplied by the caller.
A feasible layout – if it exists – is printed as JSON containing the four
required decision-variable arrays:  right, top, left, bottom.
The model uses Google OR-Tools CP-SAT (integer formulation; all given data are
integral).  If input with fractional dimensions had to be handled, a fixed-
point scaling approach could be applied without changing the logic.
"""

from ortools.sat.python import cp_model
import json
import os

# ---------------------------------------------------------------------------
# Immutable input data (exactly as given in the task                     )
# ---------------------------------------------------------------------------

deck_width = 5          # W – east–west size of the deck
deck_length = 5         # L – north–south size of the deck

n_containers = 3        # N – number of containers
width  = [5, 2, 3]      # w_i – individual widths  (east–west)
length = [1, 4, 4]      # l_i – individual lengths (north–south)
classes = [1, 1, 1]     # κ_i – class labels (1-based)

# Minimum edge-to-edge safety separation between classes *along* the deck
# (horizontal).  If the same distance were also required *across* the deck a
# second matrix would be introduced.  Here all distances are 0.
# Matrix indices are class-1.
separation_h = [        # S^{x}_{a,b}
    [0, 0],
    [0, 0]
]
# We assume no additional vertical separation is required; reuse the same
# matrix for completeness (all zeros for the present instance).
separation_v = separation_h

# ---------------------------------------------------------------------------
# Safety-distance helper functions
# ---------------------------------------------------------------------------

def sep_horizontal(i: int, j: int) -> int:
    a = classes[i] - 1
    b = classes[j] - 1
    if a < len(separation_h) and b < len(separation_h[a]):
        return separation_h[a][b]
    return 0

def sep_vertical(i: int, j: int) -> int:
    a = classes[i] - 1
    b = classes[j] - 1
    if a < len(separation_v) and b < len(separation_v[a]):
        return separation_v[a][b]
    return 0

# ---------------------------------------------------------------------------
# Model construction
# ---------------------------------------------------------------------------

model = cp_model.CpModel()

# Decision variables – tighter domains give better propagation -------------
left = []   # west  edge x-coordinate
bottom = [] # south edge y-coordinate
right = []  # east  edge x-coordinate (derived but declared for convenience)
top = []    # north edge y-coordinate

for i in range(n_containers):
    if width[i]  > deck_width  or length[i] > deck_length:
        # Impossible before modelling – print infeasible and exit early
        print(json.dumps({"right": [], "top": [], "left": [], "bottom": []}))
        raise SystemExit(0)

    li = model.NewIntVar(0, deck_width  - width[i],   f"left_{i}")
    bi = model.NewIntVar(0, deck_length - length[i],  f"bottom_{i}")
    ri = model.NewIntVar(width[i],  deck_width,       f"right_{i}")
    ti = model.NewIntVar(length[i], deck_length,      f"top_{i}")

    left.append(li)
    bottom.append(bi)
    right.append(ri)
    top.append(ti)

    # Dimension linking (no rotation)
    model.Add(ri == li + width[i])
    model.Add(ti == bi + length[i])

    # Inside-deck bounds (also enforced by domains, but added explicitly)
    model.Add(li >= 0)
    model.Add(bi >= 0)
    model.Add(ri <= deck_width)
    model.Add(ti <= deck_length)

# ---------------------------------------------------------------------------
# Non-overlap and class separations (constraints 4 & 5)
# ---------------------------------------------------------------------------
for i in range(n_containers):
    for j in range(i + 1, n_containers):
        sep_x = sep_horizontal(i, j)  # horizontal mandatory gap ≥ 0
        sep_y = sep_vertical(i, j)    # vertical   mandatory gap ≥ 0

        # Boolean literals for the four possible relative positions
        i_left_of_j = model.NewBoolVar(f"i{i}_L_j{j}")
        j_left_of_i = model.NewBoolVar(f"j{j}_L_i{i}")
        i_below_j   = model.NewBoolVar(f"i{i}_B_j{j}")
        j_below_i   = model.NewBoolVar(f"j{j}_B_i{i}")

        # Reified relations (⇒)
        model.Add(right[i] + sep_x <= left[j]).OnlyEnforceIf(i_left_of_j)
        model.Add(right[j] + sep_x <= left[i]).OnlyEnforceIf(j_left_of_i)
        model.Add(top[i]  + sep_y <= bottom[j]).OnlyEnforceIf(i_below_j)
        model.Add(top[j]  + sep_y <= bottom[i]).OnlyEnforceIf(j_below_i)

        # At least one spatial relation must hold (∨)
        model.AddBoolOr([i_left_of_j, j_left_of_i, i_below_j, j_below_i])

# ---------------------------------------------------------------------------
# Loading-sequence constraints (constraints 6 & 7)
# ---------------------------------------------------------------------------
# Containers are loaded in index order 0,1,…,N-1.
for k in range(n_containers):
    # ---- WEST side contact -------------------------------------------------
    w_wall = model.NewBoolVar(f"c{k}_touch_W_wall")  # touches west deck wall
    model.Add(left[k] == 0).OnlyEnforceIf(w_wall)
    model.Add(left[k] > 0).OnlyEnforceIf(w_wall.Not())  # reverse implication

    west_alternatives = [w_wall]

    for j in range(k):  # only containers already loaded can be touched
        w_touch_j = model.NewBoolVar(f"c{k}_touch_W_{j}")
        west_alternatives.append(w_touch_j)

        # Exact abutment: right[j] == left[k]
        model.Add(right[j] == left[k]).OnlyEnforceIf(w_touch_j)
        # Strict positive vertical overlap: bottom[k] < top[j]  ∧ bottom[j] < top[k]
        model.Add(bottom[k] < top[j]).OnlyEnforceIf(w_touch_j)
        model.Add(bottom[j] < top[k]).OnlyEnforceIf(w_touch_j)

    # At least one WEST contact literal is true
    model.AddBoolOr(west_alternatives)

    # ---- NORTH side contact ------------------------------------------------
    n_wall = model.NewBoolVar(f"c{k}_touch_N_wall")  # touches north deck wall
    model.Add(top[k] == deck_length).OnlyEnforceIf(n_wall)
    model.Add(top[k] < deck_length).OnlyEnforceIf(n_wall.Not())

    north_alternatives = [n_wall]

    for j in range(k):
        n_touch_j = model.NewBoolVar(f"c{k}_touch_N_{j}")
        north_alternatives.append(n_touch_j)

        # Exact abutment: top[k] == bottom[j]
        model.Add(top[k] == bottom[j]).OnlyEnforceIf(n_touch_j)
        # Strict positive horizontal overlap: left[k] < right[j] ∧ left[j] < right[k]
        model.Add(left[k] < right[j]).OnlyEnforceIf(n_touch_j)
        model.Add(left[j] < right[k]).OnlyEnforceIf(n_touch_j)

    model.AddBoolOr(north_alternatives)

# ---------------------------------------------------------------------------
# Solve (pure feasibility – no objective)
# ---------------------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10.0  # safety time-out
solver.parameters.num_search_workers = max(1, min(os.cpu_count() or 1, 8))

status = solver.Solve(model)

# ---------------------------------------------------------------------------
# Prepare JSON output – must contain exactly the requested keys.
# ---------------------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution = {
        "right":  [solver.Value(v) for v in right],
        "top":    [solver.Value(v) for v in top],
        "left":   [solver.Value(v) for v in left],
        "bottom": [solver.Value(v) for v in bottom]
    }
else:
    # Infeasible layout (or solver timeout without solution)
    solution = {"right": [], "top": [], "left": [], "bottom": []}

print(json.dumps(solution))
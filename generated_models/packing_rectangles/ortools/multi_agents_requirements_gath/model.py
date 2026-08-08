import json
from ortools.sat.python import cp_model

# -----------------------------------------------------------------------------
# 1. Immutable input data (exactly as provided)
# -----------------------------------------------------------------------------
widths  = [3, 4, 2, 1]  # Widths of the items
heights = [2, 3, 1, 4]  # Heights of the items
n = len(widths)

# -----------------------------------------------------------------------------
# 2. Simple bounding constants to keep domains tight
# -----------------------------------------------------------------------------
sum_widths   = sum(widths)                     # trivial upper bound on width
sum_heights  = sum(heights)                    # trivial upper bound on height
min_width    = max(widths)                     # must fit widest rectangle
area_lb      = sum(w * h for w, h in zip(widths, heights))  # theoretical area LB

# -----------------------------------------------------------------------------
# 3. Search strategy:  enumerate feasible container widths (total_x = W)
#    For every fixed width, minimise container height (total_y).
# -----------------------------------------------------------------------------

best_area    = None
best_total_x = None
best_total_y = None
best_pos_x   = None
best_pos_y   = None

for W in range(min_width, sum_widths + 1):
    model = cp_model.CpModel()

    # Decision variables ------------------------------------------------------
    total_x = model.NewIntVar(W, W, "total_x")          # fixed to W
    total_y = model.NewIntVar(1, sum_heights, "total_y")

    pos_x = [model.NewIntVar(0, W - widths[i],  f"pos_x_{i}") for i in range(n)]
    pos_y = [model.NewIntVar(0, sum_heights - heights[i], f"pos_y_{i}") for i in range(n)]

    # Containment constraints -------------------------------------------------
    for i in range(n):
        model.Add(pos_x[i] + widths[i]  <= total_x)     # right edge inside
        model.Add(pos_y[i] + heights[i] <= total_y)     # top   edge inside

    # Non-overlap via global 2-D constraint -----------------------------------
    x_intervals = []
    y_intervals = []
    for i in range(n):
        end_x = model.NewIntVar(0, W,           f"end_x_{i}")
        end_y = model.NewIntVar(0, sum_heights, f"end_y_{i}")
        model.Add(end_x == pos_x[i] + widths[i])
        model.Add(end_y == pos_y[i] + heights[i])

        x_intervals.append(model.NewIntervalVar(pos_x[i], widths[i], end_x, f"x_int_{i}"))
        y_intervals.append(model.NewIntervalVar(pos_y[i], heights[i], end_y, f"y_int_{i}"))

    model.AddNoOverlap2D(x_intervals, y_intervals)

    # Objective: minimise container height for this width ---------------------
    model.Minimize(total_y)

    # Solve -------------------------------------------------------------------
    solver = cp_model.CpSolver()
    # For this tiny instance no limit is strictly necessary, but place a small
    # one to guarantee termination on larger inputs.
    solver.parameters.max_time_in_seconds = 10

    status = solver.Solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        H = solver.Value(total_y)
        area = W * H

        if best_area is None or area < best_area:
            best_area    = area
            best_total_x = W
            best_total_y = H
            best_pos_x   = [solver.Value(px) for px in pos_x]
            best_pos_y   = [solver.Value(py) for py in pos_y]

        # Cannot beat the theoretical lower bound – stop early.
        if status == cp_model.OPTIMAL and best_area == area_lb:
            break

# -----------------------------------------------------------------------------
# 4. Emit solution in the required JSON format
# -----------------------------------------------------------------------------
if best_area is None:
    raise RuntimeError("No feasible packing found (should never occur).")

result = {
    "total_y": best_total_y,
    "pos_x": best_pos_x,
    "pos_y": best_pos_y,
    "total_x": best_total_x,
}

print(json.dumps(result))
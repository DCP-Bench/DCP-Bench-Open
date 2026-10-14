"""Perfect square placement: place squares of given sides, without overlap, inside a large square so that they cover it exactly."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    base = instance["base"]    # side of the large square
    sides = instance["sides"]  # sides of the small squares
    squares = range(len(sides))

    model = gp.Model("perfect_square_placement")
    # A satisfaction problem: the solver is told to look for a feasible placement.
    model.Params.MIPFocus = 1

    # (x[i], y[i]) is the lower-left corner of square i. A square lies inside the large square,
    # so its corner leaves room for the square's side.
    x = model.addVars(squares, lb=0, ub=base, vtype=GRB.INTEGER, name="x")
    y = model.addVars(squares, lb=0, ub=base, vtype=GRB.INTEGER, name="y")
    for i in squares:
        model.addConstr(x[i] + sides[i] <= base, name=f"inside_x[{i}]")
        model.addConstr(y[i] + sides[i] <= base, name=f"inside_y[{i}]")

    # No two squares overlap: for each pair, one is entirely left of, right of, below or above
    # the other. Each branch is posted with a big-M of `base`, which is the most the left side
    # of a branch can exceed its right side by, given the bounds above.
    for a in squares:
        for b in range(a + 1, len(sides)):
            left_of = model.addVar(vtype=GRB.BINARY, name=f"a_left_of_b[{a},{b}]")
            right_of = model.addVar(vtype=GRB.BINARY, name=f"a_right_of_b[{a},{b}]")
            below = model.addVar(vtype=GRB.BINARY, name=f"a_below_b[{a},{b}]")
            above = model.addVar(vtype=GRB.BINARY, name=f"a_above_b[{a},{b}]")
            model.addConstr(x[a] + sides[a] <= x[b] + base * (1 - left_of), name=f"left[{a},{b}]")
            model.addConstr(x[b] + sides[b] <= x[a] + base * (1 - right_of), name=f"right[{a},{b}]")
            model.addConstr(y[a] + sides[a] <= y[b] + base * (1 - below), name=f"below[{a},{b}]")
            model.addConstr(y[b] + sides[b] <= y[a] + base * (1 - above), name=f"above[{a},{b}]")
            model.addConstr(left_of + right_of + below + above >= 1, name=f"separate[{a},{b}]")

    return model, {"x_coords": [x[i] for i in squares], "y_coords": [y[i] for i in squares]}

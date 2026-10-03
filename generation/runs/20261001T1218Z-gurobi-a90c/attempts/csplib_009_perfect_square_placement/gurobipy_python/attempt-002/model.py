"""Perfect square placement: place squares of given sides, without overlap, inside a large square so that they cover it exactly."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    base = instance["base"]    # side of the large square
    sides = instance["sides"]  # sides of the small squares
    squares = range(len(sides))

    model = gp.Model("perfect_square_placement")

    # (x[i], y[i]) is the lower-left corner of square i. A square lies inside the large square,
    # so its corner is at most base - side along each axis (a variable bound, not a row).
    x = model.addVars(squares, lb=0, ub=[base - s for s in sides], vtype=GRB.INTEGER, name="x")
    y = model.addVars(squares, lb=0, ub=[base - s for s in sides], vtype=GRB.INTEGER, name="y")

    # No two squares overlap: one is entirely left of, right of, below or above the other.
    # Two binaries choose among the four cases: apart_x says the pair is separated along x
    # (else along y), b_first says b comes first along that axis. Each case is relaxed by
    # big-M = base, the most its left side can exceed its right side by.
    for a in squares:
        for b in range(a + 1, len(sides)):
            apart_x = model.addVar(vtype=GRB.BINARY, name=f"apart_x[{a},{b}]")
            b_first = model.addVar(vtype=GRB.BINARY, name=f"b_first[{a},{b}]")
            model.addConstr(x[a] + sides[a] <= x[b] + base * (1 - apart_x) + base * b_first, name=f"a_left_of_b[{a},{b}]")
            model.addConstr(x[b] + sides[b] <= x[a] + base * (1 - apart_x) + base * (1 - b_first), name=f"b_left_of_a[{a},{b}]")
            model.addConstr(y[a] + sides[a] <= y[b] + base * apart_x + base * b_first, name=f"a_below_b[{a},{b}]")
            model.addConstr(y[b] + sides[b] <= y[a] + base * apart_x + base * (1 - b_first), name=f"b_below_a[{a},{b}]")

    # Implied by exact covering, and added to narrow the search: the cells just left of a
    # square that is not at the left border are covered by some other square, which cannot
    # reach into this one, so that square's right side is exactly this square's left side.
    # The same holds below a square that is not at the bottom border. Every exact covering
    # satisfies this, so no placement is lost.
    for i in squares:
        for coord, axis in ((x, "x"), (y, "y")):
            at_border = model.addVar(vtype=GRB.BINARY, name=f"{axis}_border[{i}]")
            model.addConstr((at_border == 1) >> (coord[i] == 0), name=f"{axis}_at_border[{i}]")
            touches = [at_border]
            for j in squares:
                if j != i:
                    t = model.addVar(vtype=GRB.BINARY, name=f"{axis}_touch[{i},{j}]")
                    model.addConstr((t == 1) >> (coord[i] - coord[j] == sides[j]), name=f"{axis}_touch[{i},{j}]")
                    touches.append(t)
            model.addConstr(gp.quicksum(touches) >= 1, name=f"{axis}_supported[{i}]")

    return model, {"x_coords": [x[i] for i in squares], "y_coords": [y[i] for i in squares]}

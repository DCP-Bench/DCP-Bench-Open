"""Ages of the sons: three ages with product 36 whose sum does not identify them alone, but does once there is a single oldest son."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: the product 36 and the age range 0..36 are the
    # puzzle's own, mirrored from the reference.
    product = 36
    max_age = 36

    model = gp.Model("ages_of_the_sons")

    # The product of three ages is not linear. Instead, list every triple of ages in
    # 0..36 (largest first) whose product is 36, and choose one triple: this is the
    # constraint 36 == A1 * A2 * A3 written as a table.
    triples = [(a, b, c) for a in range(max_age + 1) for b in range(a + 1) for c in range(b + 1)
               if a * b * c == product]

    # pick_a[t]: the sons' ages are triple t. The oldest son is strictly the oldest
    # (A1 > A2 >= A3), since he is "the oldest son".
    options_a = [t for t in triples if t[0] > t[1]]
    pick_a = model.addVars(len(options_a), vtype=GRB.BINARY, name="pick_a")
    model.addConstr(pick_a.sum() == 1, name="one_answer")
    A = [gp.quicksum(t[k] * pick_a[i] for i, t in enumerate(options_a)) for k in range(3)]

    # pick_b[t]: another triple with product 36 (B1 >= B2 >= B3) that the mathematician
    # could not tell apart after the second clue.
    pick_b = model.addVars(len(triples), vtype=GRB.BINARY, name="pick_b")
    model.addConstr(pick_b.sum() == 1, name="one_alternative")
    B = [gp.quicksum(t[k] * pick_b[i] for i, t in enumerate(triples)) for k in range(3)]

    # The sum of the ages (the number of windows) is the same for both triples.
    model.addConstr(gp.quicksum(A) == gp.quicksum(B), name="same_windows")

    # The alternative has a different oldest age: A1 != B1, as one strict inequality or the other.
    lower = model.addVar(vtype=GRB.BINARY, name="b1_lower")
    model.addConstr((lower == 1) >> (B[0] <= A[0] - 1))
    model.addConstr((lower == 0) >> (B[0] >= A[0] + 1))

    # The outputs are integer variables equal to the chosen ages.
    a1 = model.addVar(lb=0, ub=max_age, vtype=GRB.INTEGER, name="A1")
    a2 = model.addVar(lb=0, ub=max_age, vtype=GRB.INTEGER, name="A2")
    a3 = model.addVar(lb=0, ub=max_age, vtype=GRB.INTEGER, name="A3")
    model.addConstr(a1 == A[0])
    model.addConstr(a2 == A[1])
    model.addConstr(a3 == A[2])

    return model, {"A1": a1, "A2": a2, "A3": a3}

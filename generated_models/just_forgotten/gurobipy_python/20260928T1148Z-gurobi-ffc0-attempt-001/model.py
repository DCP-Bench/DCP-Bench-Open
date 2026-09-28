"""Just forgotten: recover an account number that uses each digit 0..n-1 once, knowing how many digits of each tried set were in place."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    sets = instance["sets"]  # the numbers Joe tried
    correct = instance["num_correct_digits"]
    n = len(sets[0])
    positions = range(n)
    digits = range(n)

    model = gp.Model("just_forgotten")

    # digit_at[i, d] is 1 when position i of the account number holds digit d.
    digit_at = model.addVars(positions, digits, vtype=GRB.BINARY, name="digit_at")

    # Every position holds one digit, and every digit 0..n-1 is used once.
    for i in positions:
        model.addConstr(digit_at.sum(i, "*") == 1, name=f"position[{i}]")
    for d in digits:
        model.addConstr(digit_at.sum("*", d) == 1, name=f"digit[{d}]")

    # In each tried set, exactly the given number of digits are in their correct position.
    for k, tried in enumerate(sets):
        model.addConstr(gp.quicksum(digit_at[i, tried[i]] for i in positions if tried[i] in digits)
                        == correct, name=f"set[{k}]")

    x = [gp.quicksum(d * digit_at[i, d] for d in digits) for i in positions]
    return model, {"x": x}

# Climbing stairs: climb a stair of n steps, taking between m1 and m2 steps per move.
# Output steps[i] is the number of steps taken at move i: a value in m1..m2 when a move
# is made, or 0 once the top is reached and no move is taken.
import mip


def build(instance):
    n = instance["n"]
    m1 = instance["m1"]
    m2 = instance["m2"]
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    steps = [model.add_var(f"steps_{i}", lb=0, ub=m2, var_type=mip.INTEGER) for i in range(n)]
    moved = [model.add_var(f"moved_{i}", var_type=mip.BINARY) for i in range(n)]

    # You can take only m1 to m2 steps at a time, or 0 steps once the top is reached.
    for i in range(n):
        model.add_constr(steps[i] >= m1 * moved[i], f"min_step_{i}")
        model.add_constr(steps[i] <= m2 * moved[i], f"max_step_{i}")

    # Once no move is taken (the top is reached), no later move is taken.
    for i in range(n - 1):
        model.add_constr(moved[i] >= moved[i + 1], f"stop_{i}")

    # We want to climb a stair of n steps, so the moves add up to exactly n.
    model.add_constr(mip.xsum(steps) == n, "climb_n_steps")

    return model, {"steps": steps}

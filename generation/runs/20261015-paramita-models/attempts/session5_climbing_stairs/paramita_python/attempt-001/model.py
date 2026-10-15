# Climbing stairs: climb a stair of n steps, taking between m1 and m2 steps
# at a time. Output the steps taken at each move (0 once the top is reached).
from paramita.modelling import Bool, If


def build(instance):
    n, m1, m2 = instance["n"], instance["m1"], instance["m2"]
    values = list(range(m1, m2 + 1))

    # Move i is one-hot over {0} + [m1..m2]: x[i][v] means move i takes v steps,
    # and x[i][0] means no steps are taken (the top has been reached).
    x = [{v: Bool(f"move_{i}_takes_{v}") for v in [0] + values} for i in range(n)]

    cons = []
    # each move takes exactly one amount of steps
    cons += [sum(x[i].values()) == 1 for i in range(n)]

    # no steps are taken at a move only after the top is reached:
    # once a move takes 0 steps, every later move takes 0 steps
    cons += [If(x[i][0], x[i + 1][0]) for i in range(n - 1)]

    # the moves together climb exactly n steps
    cons += [sum(v * x[i][v] for i in range(n) for v in values) == n]

    # the number of steps taken at each move (0 after the top is reached)
    steps = [sum(v * x[i][v] for v in values) for i in range(n)]

    return cons, {"steps": steps}

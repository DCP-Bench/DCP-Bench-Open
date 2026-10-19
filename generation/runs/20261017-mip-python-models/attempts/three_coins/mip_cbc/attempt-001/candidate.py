# Three coins lie on a table in the order given by the instance (init, 1 = tails, 0 = heads).
# In precisely num_moves moves make them all face either heads or tails. Each move
# consists of choosing one coin and flipping it over. The output steps[t][i] is True for
# tails: row 0 is the initial state and row t is the state after move t.
import mip


def build(instance):
    init = instance["init"]
    num_moves = instance["num_moves"]
    n = len(init)
    rows = num_moves + 1

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # state[t][i] = 1 when coin i shows tails in row t
    state = [
        [model.add_var(f"state_{t}_{i}", var_type=mip.BINARY) for i in range(n)]
        for t in range(rows)
    ]
    # flip[t][i] = 1 when move t flips coin i (flip[0] is unused)
    flip = [None] + [
        [model.add_var(f"flip_{t}_{i}", var_type=mip.BINARY) for i in range(n)]
        for t in range(1, rows)
    ]

    # The coins start in the order given by the instance.
    for i in range(n):
        model.add_constr(state[0][i] == init[i])

    # Each move consists of choosing one coin and flipping it over.
    for t in range(1, rows):
        model.add_constr(mip.xsum(flip[t][i] for i in range(n)) == 1)

    # Flipping a coin over changes its face; a coin not chosen keeps its face.
    # New face = old face XOR flipped, written as four linear inequalities.
    for t in range(1, rows):
        for i in range(n):
            a = state[t - 1][i]
            b = state[t][i]
            c = flip[t][i]
            model.add_constr(b <= a + c)
            model.add_constr(b >= a - c)
            model.add_constr(b >= c - a)
            model.add_constr(b <= 2 - a - c)

    # Make them face either all heads or all tails at the end.
    last = rows - 1
    for i in range(1, n):
        model.add_constr(state[last][i] == state[last][0])

    steps = [[state[t][i] for i in range(n)] for t in range(rows)]
    return model, {"steps": steps}

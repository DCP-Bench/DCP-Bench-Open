# Three coins on a table: flip coins so that, in precisely num_moves moves,
# all coins face the same way (all heads or all tails). Each move flips one coin.
# steps[t][c] is True for tails, False for heads; row 0 is the initial state.
import cvc5.pythonic as cz


def build(instance):
    init = instance["init"]
    num_moves = instance["num_moves"]
    n = len(init)
    steps = [[cz.Bool(f"s_{t}_{c}") for c in range(n)] for t in range(num_moves + 1)]
    constraints = []

    # The coins start in the order given by the instance (1 = tails, 0 = heads).
    for c in range(n):
        if init[c] == 1:
            constraints.append(steps[0][c])
        else:
            constraints.append(cz.Not(steps[0][c]))

    # Each move chooses one coin and flips it over: exactly one coin differs
    # between consecutive rows.
    for t in range(num_moves):
        diffs = [cz.If(cz.Not(steps[t][c] == steps[t + 1][c]), 1, 0) for c in range(n)]
        constraints.append(cz.Sum(diffs) == 1)

    # After the moves, all coins face either all heads or all tails.
    last = steps[num_moves]
    constraints.append(
        cz.Or(
            cz.And([b for b in last]),
            cz.And([cz.Not(b) for b in last]),
        )
    )

    return constraints, {"steps": steps}

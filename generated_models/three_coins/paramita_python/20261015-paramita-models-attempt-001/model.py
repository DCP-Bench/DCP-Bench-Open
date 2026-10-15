# Three coins, three moves. True means tails (1), False means heads (0).
# steps[k] is the state of the three coins after k moves; steps[0] is the initial state.
from paramita.modelling import Bool, If, Iff

COINS = 3


def build(instance):
    init = instance["init"]
    moves = instance["num_moves"]

    # steps[k][i] = coin i shows tails after k moves
    steps = [[Bool(f"s_{k}_{i}") for i in range(COINS)] for k in range(moves + 1)]
    # chosen[k][i] = move k flips coin i
    chosen = [[Bool(f"m_{k}_{i}") for i in range(COINS)] for k in range(moves)]

    cons = []

    # the coins lie on the table in the initial order tails, heads, tails
    for i in range(COINS):
        cons.append(steps[0][i] if init[i] == 1 else ~steps[0][i])

    # each move consists of choosing exactly one coin
    for k in range(moves):
        cons.append(sum(chosen[k]) == 1)

    # each move flips the chosen coin and leaves the others as they are
    for k in range(moves):
        for i in range(COINS):
            cons.append(If(chosen[k][i], Iff(steps[k + 1][i], ~steps[k][i])))
            cons.append(If(~chosen[k][i], Iff(steps[k + 1][i], steps[k][i])))

    # the final state has all coins facing heads or all facing tails
    last = steps[moves]
    cons.append(Iff(last[0], last[1]))
    cons.append(Iff(last[1], last[2]))

    return cons, {"steps": steps}

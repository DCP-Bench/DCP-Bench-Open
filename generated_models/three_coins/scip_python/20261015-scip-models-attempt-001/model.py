# Three coins: flip coins one at a time, in exactly the given number of moves, until all coins face the same way (all heads or all tails).
from pyscipopt import Model, quicksum


def build(instance):
    init = instance["init"]  # True where the coin starts tails
    moves = instance["num_moves"]
    k = len(init)  # number of coins
    states = range(moves + 1)  # state 0 is the start, state moves is the end
    coins = range(k)

    m = Model()

    # s[t, i] = 1 if coin i shows tails in state t
    s = {(t, i): m.addVar(name=f"s_{t}_{i}", vtype="B") for t in states for i in coins}
    # f[t, i] = 1 if move t flips coin i
    f = {(t, i): m.addVar(name=f"f_{t}_{i}", vtype="B") for t in range(moves) for i in coins}

    # the start state is the given one
    for i in coins:
        m.addCons(s[0, i] == (1 if init[i] else 0))

    # each move chooses exactly one coin and flips it
    for t in range(moves):
        m.addCons(quicksum(f[t, i] for i in coins) == 1)

    # a flipped coin changes face, an unflipped coin keeps its face
    for t in range(moves):
        for i in coins:
            m.addConsXor([s[t, i], f[t, i], s[t + 1, i]], False)

    # the final state has all coins facing the same way
    for i in coins:
        m.addCons(s[moves, i] == s[moves, 0])

    # the output gives the coin faces in each state (True = tails)
    steps = [[s[t, i] for i in coins] for t in states]
    return m, {"steps": steps}

# Climbing stairs: climb a stair of n steps in moves of m1 to m2 steps each. steps[i] is the
# number of steps taken in move i; once the top is reached the remaining moves are 0.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]    # steps in the stair; also the largest number of moves (all of one step)
    m1 = instance["m1"]  # fewest steps in one move
    m2 = instance["m2"]  # most steps in one move

    pool = IDPool()
    # steps[i] = steps taken in move i: 0 (no move) or m1..m2
    steps = [Integer(f"steps{i}", 0, m2, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=steps, vpool=pool)

    # the moves add up to the whole stair
    engine.add_linear(sum(steps) == n)

    cnf = engine.clausify()

    # a move takes between m1 and m2 steps, or 0 if no move is made: the values 1..m1-1 are excluded
    for move in steps:
        for value in range(1, m1):
            cnf.append([-move.equals(value)])

    # once a move is 0 all later moves are 0 (trailing zeros): a 0 is followed by a 0, which makes
    # every move after the first 0 equal to 0
    for i in range(1, n):
        cnf.append([-steps[i - 1].equals(0), steps[i].equals(0)])

    return cnf, {"steps": steps}

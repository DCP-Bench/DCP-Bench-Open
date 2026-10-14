"""Age changing (Enigma 1224): applying the four operations +2, /8, -3 and *7 in some order
to my age gives my husband's age, and applying the same four operations in a different
order to his age gives mine. What are our two ages?

The model reports my age m and my husband's age h.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its constants are below

    # Problem constants, mirrored from the reference: ages are 16..120 and every
    # intermediate value of the calculation lies in 1..1000.
    age_low, age_high = 16, 120
    value_low, value_high = 1, 1000
    # Each operation as (a, b, c) meaning a * new + b * old + c == 0:
    # +2 is new = old + 2, /8 is 8 * new = old, -3 is new = old - 3, *7 is new = 7 * old.
    operations = [(1, -1, -2), (8, -1, 0), (1, -1, 3), (1, -7, 0)]
    n = len(operations)

    problem = pulp.LpProblem("age_changing", pulp.LpMinimize)  # satisfaction

    m = pulp.LpVariable("m", age_low, age_high, cat="Integer")  # my age
    h = pulp.LpVariable("h", age_low, age_high, cat="Integer")  # my husband's age

    # hlist: the values from my age to his; mlist: the values from his age to mine
    hlist = [pulp.LpVariable(f"hlist_{i}", value_low, value_high, cat="Integer")
             for i in range(n + 1)]
    mlist = [pulp.LpVariable(f"mlist_{i}", value_low, value_high, cat="Integer")
             for i in range(n + 1)]

    # order1[i][k] = 1 if operation k is applied at step i on the way from my age to his;
    # order2 likewise from his age to mine. Each order uses every operation once.
    order1 = [[pulp.LpVariable(f"order1_{i}_{k}", cat="Binary") for k in range(n)]
              for i in range(n)]
    order2 = [[pulp.LpVariable(f"order2_{i}_{k}", cat="Binary") for k in range(n)]
              for i in range(n)]
    for order in (order1, order2):
        for i in range(n):
            problem += pulp.lpSum(order[i]) == 1
        for k in range(n):
            problem += pulp.lpSum(order[i][k] for i in range(n)) == 1

    # the two orders differ: same[i][k] is 1 when both orders apply operation k at step i,
    # and not all four steps may agree
    same = [[pulp.LpVariable(f"same_{i}_{k}", cat="Binary") for k in range(n)]
            for i in range(n)]
    for i in range(n):
        for k in range(n):
            problem += same[i][k] >= order1[i][k] + order2[i][k] - 1
    problem += pulp.lpSum(same[i][k] for i in range(n) for k in range(n)) <= n - 1

    # start with my age and end with my husband's, and the other way round
    problem += hlist[0] == m
    problem += hlist[n] == h
    problem += mlist[0] == h
    problem += mlist[n] == m

    # the operation chosen at each step turns the value before it into the value after it.
    # The slack of a * new + b * old + c over the value range is the big-M that frees the
    # constraint when the operation is not chosen.
    def span(a, b, c):
        ends = [a * new + b * old + c for new in (value_low, value_high)
                for old in (value_low, value_high)]
        return min(ends), max(ends)

    for values, order in ((hlist, order1), (mlist, order2)):
        for i in range(n):
            for k, (a, b, c) in enumerate(operations):
                low, high = span(a, b, c)
                expression = a * values[i + 1] + b * values[i] + c
                problem += expression <= high * (1 - order[i][k])
                problem += expression >= low * (1 - order[i][k])

    return problem, {"m": m, "h": h}

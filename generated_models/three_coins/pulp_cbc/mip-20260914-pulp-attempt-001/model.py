import pulp


def build(instance):
    initial, num_moves = instance["init"], instance["num_moves"]
    coins = range(len(initial))
    problem = pulp.LpProblem("three_coins", pulp.LpMinimize)
    steps = [[pulp.LpVariable(f"s_{m}_{j}", cat="Binary") for j in coins]
             for m in range(num_moves + 1)]
    for j in coins:
        problem += steps[0][j] == initial[j]
    for m in range(1, num_moves + 1):
        changed = []
        for j in coins:
            before, after = steps[m - 1][j], steps[m][j]
            flip = pulp.LpVariable(f"flip_{m}_{j}", cat="Binary")
            problem += flip >= before - after
            problem += flip >= after - before
            problem += flip <= before + after
            problem += flip <= 2 - before - after
            changed.append(flip)
        problem += pulp.lpSum(changed) == 1
    # The last row is all heads or all tails.
    all_tails = pulp.LpVariable("all_tails", cat="Binary")
    problem += pulp.lpSum(steps[num_moves]) == len(initial) * all_tails
    return problem, {"steps": steps}

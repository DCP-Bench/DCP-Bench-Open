import pulp


def build(instance):
    """Coin change: carry as few coins as possible while still being able to
    pay every amount from 1 up to max_amount_to_pay - 1 exactly.
    """
    denominations = instance["denominations"]
    max_amount = instance["max_amount_to_pay"]
    n = len(denominations)

    problem = pulp.LpProblem("coin3", pulp.LpMinimize)
    x = [pulp.LpVariable(f"x{i}", 0, max_amount, cat="Integer")
         for i in range(n)]

    # One witness selection per payable amount, drawn from the coins carried.
    for amount in range(1, max_amount):
        use = [pulp.LpVariable(f"u{amount}_{i}", 0, max_amount, cat="Integer")
               for i in range(n)]
        for i in range(n):
            problem += use[i] <= x[i]
        problem += pulp.lpSum(denominations[i] * use[i]
                              for i in range(n)) == amount

    problem += pulp.lpSum(x)

    return problem, {"x": x}

# Coins: find the smallest set of coins (from the given denominations) with which
# every amount below a maximum can be paid exactly.
import z3


def build(instance):
    denominations = instance["denominations"]        # value of each kind of coin
    max_amount = instance["max_amount_to_pay"]       # amounts 1..max_amount-1 must be payable
    n = len(denominations)

    # x[i] is the number of coins of denomination i that we own.
    x = [z3.Int(f"x_{i}") for i in range(n)]
    # num_coins is the total number of coins owned.
    num_coins = z3.Int("num_coins")

    solver = z3.Solver()

    # Bounds as in the reference: at most max_amount coins of each kind and in total.
    for xi in x:
        solver.add(xi >= 0, xi <= max_amount)
    solver.add(num_coins >= 0, num_coins <= max_amount)

    # The number of coins to be minimised is the sum over all kinds.
    solver.add(num_coins == z3.Sum(x))

    # Every amount from 1 to max_amount - 1 can be paid: for each amount there is a
    # selection of coins (used[i] of kind i) worth exactly that amount, which does
    # not use more coins of a kind than we own.
    for amount in range(1, max_amount):
        used = [z3.Int(f"used_{amount}_{i}") for i in range(n)]
        for i in range(n):
            # Paying `amount` cannot use more than amount // value coins of a kind; the
            # bound follows from the sum below and narrows the search Z3 does on it.
            solver.add(used[i] >= 0, used[i] <= min(max_amount, amount // denominations[i]),
                       used[i] <= x[i])
        solver.add(z3.Sum([used[i] * denominations[i] for i in range(n)]) == amount)

    # Fewest coins possible.
    return solver, {"x": x}, ("minimize", num_coins)

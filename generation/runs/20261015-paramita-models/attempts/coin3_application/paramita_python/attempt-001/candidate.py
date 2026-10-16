# Coin application: pay every amount below a maximum with the fewest coins.
# Given denominations and a maximum amount M, choose how many coins x[i] of
# each denomination to take, so that every amount 1..M-1 can be paid exactly
# with those coins, and the total number of coins is as small as possible.
from paramita.modelling import Bool, If


def build(instance):
    denoms = instance["denominations"]
    top = instance["max_amount_to_pay"]  # every amount 1..top-1 must be payable
    cons = []

    # x[i] = number of coins of denomination i.
    # Unary: x_ge_i_k means x[i] >= k+1, for k up to the bound below.
    # The bound is (top-1) // d: an optimal solution never needs more coins of
    # one denomination than the largest amount can use.
    xs = []
    for i, d in enumerate(denoms):
        u = (top - 1) // d
        bits = [Bool(f"x_{i}_ge_{k}") for k in range(1, u + 1)]
        for k in range(len(bits) - 1):
            cons.append(If(bits[k + 1], bits[k]))  # x >= k+2 implies x >= k+1
        xs.append(sum(bits) if bits else 0)

    # Every amount a from 1 to top-1 can be paid exactly with the coins taken.
    # p[a][i][k] (k = 1..a//d) is a coin of denomination i used for amount a;
    # the coins used for a must add up to a, and each denomination used for a
    # must not exceed the number of coins x[i] taken.
    for a in range(1, top):
        terms = []
        for i, d in enumerate(denoms):
            k_max = a // d
            if k_max == 0:
                continue  # a coin larger than a cannot be used for a
            p = [Bool(f"p_{a}_{i}_{k}") for k in range(1, k_max + 1)]
            used = sum(p)
            terms.append(d * used)
            cons.append(used <= xs[i])  # coins used for a are among those taken
        # the coins used for amount a add up to a
        cons.append(sum(terms) == a)

    # Objective: minimise the total number of coins taken.
    total = sum(xs)
    return cons, {"x": xs}, ("minimize", total)

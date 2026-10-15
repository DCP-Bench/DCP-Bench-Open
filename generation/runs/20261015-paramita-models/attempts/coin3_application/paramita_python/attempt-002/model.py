# Coin application: pay every amount below a maximum with the fewest coins.
# Given denominations and a maximum amount M, choose how many coins x[i] of
# each denomination to take, so that every amount 1..M-1 can be paid exactly
# with those coins, and the total number of coins is as small as possible.
from paramita.modelling import Bool, And, Or, If, Iff


def build(instance):
    denoms = instance["denominations"]
    top = instance["max_amount_to_pay"]  # every amount 1..top-1 must be payable
    cons = []

    # x[i] = number of coins of denomination i.
    # Unary: x_i_ge_k means x[i] >= k, for k = 1..u with the bound below.
    # The bound is (top-1) // d: an optimal solution never needs more coins of
    # one denomination than the largest amount can use.
    xs = []
    xge = []
    for i, d in enumerate(denoms):
        u = (top - 1) // d
        bits = [Bool(f"x_{i}_ge_{k}") for k in range(1, u + 1)]
        for k in range(len(bits) - 1):
            cons.append(If(bits[k + 1], bits[k]))  # x >= k+1 implies x >= k
        xge.append(bits)
        xs.append(sum(bits) if bits else 0)

    # Reachability over the denominations. r[j][v] holds when the value v can be
    # paid exactly with the first j denominations, using at most x[i] coins of
    # each denomination i. Layer 0 pays only the value 0.
    prev = [Bool(f"r_0_{v}") for v in range(top)]
    cons.append(prev[0])
    cons += [~prev[v] for v in range(1, top)]

    # Adding denomination j: value v is paid when, for some k coins of
    # denomination j (k = 0 or more, at most x[j] of them), the value v - k*d
    # is paid with the earlier denominations.
    for j, d in enumerate(denoms):
        cur = [Bool(f"r_{j + 1}_{v}") for v in range(top)]
        for v in range(top):
            options = []
            for k in range(0, v // d + 1):
                if k > len(xge[j]):
                    break
                base = prev[v - k * d]
                if k == 0:
                    options.append(base)
                else:
                    options.append(And(base, xge[j][k - 1]))  # x[j] >= k
            if len(options) == 1:
                cons.append(Iff(cur[v], options[0]))
            else:
                cons.append(Iff(cur[v], Or(options)))
        prev = cur

    # Every amount a from 1 to top-1 can be paid exactly with the coins taken.
    for a in range(1, top):
        cons.append(prev[a])

    # Objective: minimise the total number of coins taken.
    total = sum(xs)
    return cons, {"x": xs}, ("minimize", total)

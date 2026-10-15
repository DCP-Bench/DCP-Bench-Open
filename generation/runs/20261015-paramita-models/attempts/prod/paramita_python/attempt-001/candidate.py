# Production planning: choose the quantities X[j] of the products j so that the total
# profit is maximised, subject to one shared time budget and per-product upper bounds.
from math import lcm

from paramita.modelling import Bool, If


def build(instance):
    a, c, u, b = instance["a"], instance["c"], instance["u"], instance["b"]
    products = range(len(a))

    # Each quantity X[j] is an integer in 0..u[j], written in unary: ge[j][k] is true
    # exactly when X[j] >= k + 1. There are u[j] such bits, so 0 <= X[j] <= u[j] holds
    # by construction.
    ge = [[Bool(f"ge_{j}_{k}") for k in range(u[j])] for j in products]

    cons = []
    # the bits of X[j] are an order: X[j] >= k + 2 implies X[j] >= k + 1
    for j in products:
        for k in range(u[j] - 1):
            cons.append(If(ge[j][k + 1], ge[j][k]))

    # X[j] as the sum of its unary bits
    x = [sum(ge[j]) for j in products]

    # the sum of (1/a[j]) * X[j] over all products must be at most b (the time budget).
    # Multiplying both sides by L = lcm(a) gives integer coefficients L / a[j].
    L = lcm(*a)
    cons.append(sum((L // a[j]) * bit for j in products for bit in ge[j]) <= L * b)

    # the total profit is the sum of c[j] * X[j] over all products
    total_profit = sum(c[j] * bit for j in products for bit in ge[j])

    return cons, {"x": x, "total_profit": total_profit}, ("maximize", total_profit)

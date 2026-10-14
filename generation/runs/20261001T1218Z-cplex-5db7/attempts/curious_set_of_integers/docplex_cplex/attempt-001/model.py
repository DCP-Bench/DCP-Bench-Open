"""Curious set of integers (Martin Gardner): in the set 1, 3, 8, 120 the product of any two
members is one less than a perfect square. Find a fifth number, at least 0, that keeps this
property.
"""
import math

from docplex.mp.model import Model


def build(instance):
    n = instance["n"]
    max_val = instance["max_val"]
    # The four known members come from the problem statement, mirrored from the reference.
    # The statement asks for one more number, so the set has n == 5 members.
    known = [1, 3, 8, 120]
    if n != len(known) + 1:
        raise ValueError("the problem adds exactly one number to the four known ones")

    model = Model("curious_set_of_integers")

    number = model.integer_var(0, max_val, name="number")

    # All members are different: the new number is none of the known ones.
    for k in known:
        model.add(number != k)

    # The product of two known members plus one is a square whose root is at most max_val
    # (the reference's domain for the root). This is fixed data, checked here.
    for a in known:
        for b in known:
            if a != b:
                root = math.isqrt(a * b + 1)
                if root * root != a * b + 1 or root > max_val:
                    model.add_constraint(model.sum([]) == 1)  # no such set exists

    # For each known member k, k * number + 1 is a square p * p with p in 0..max_val.
    # Since number <= max_val, p is at most isqrt(k * max_val + 1). CPLEX refuses p * p, so
    # p is written in binary, p = sum 2^i bit_i, and p * p = sum_i sum_j 2^(i+j) bit_i bit_j,
    # where each product of two bits is a binary that is 1 exactly when both bits are.
    for k in known:
        hi = min(max_val, math.isqrt(k * max_val + 1))
        width = hi.bit_length()
        bit = [model.binary_var(name=f"root_{k}_bit_{i}") for i in range(width)]
        model.add_constraint(model.sum(2 ** i * bit[i] for i in range(width)) <= hi)
        square_terms = []
        for i in range(width):
            square_terms.append(2 ** (2 * i) * bit[i])
            for j in range(i + 1, width):
                both = model.binary_var(name=f"root_{k}_bits_{i}_{j}")
                model.add_constraint(both <= bit[i])
                model.add_constraint(both <= bit[j])
                model.add_constraint(both >= bit[i] + bit[j] - 1)
                square_terms.append(2 * 2 ** (i + j) * both)
        # The product of k and the new number is one less than this square.
        model.add_constraint(k * number + 1 == model.sum(square_terms))

    return model, {"number": number}

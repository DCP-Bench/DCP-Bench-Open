"""Circling the squares (Dudeney, Amusements in Mathematics 43): place ten different numbers
in a circle so that the sum of the squares of any two adjacent numbers equals the sum of
the squares of the two numbers diametrically opposite them, with A=16, B=2, F=8, G=14 given.

The model reports the ten numbers A, B, C, D, E, F, G, H, I, K.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its givens are below

    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]
    values = range(1, 100)  # no number needs more than two figures (reference domain 1..99)
    given = {"A": 16, "B": 2, "F": 8, "G": 14}  # the four numbers that must stand as they are

    problem = pulp.LpProblem("circling_squares", pulp.LpMinimize)  # satisfaction

    # is_value[s][v] = 1 if square s holds the number v. Squares are not linear, so each
    # number is chosen from its range and its square is read off the same binaries.
    is_value = {s: {v: pulp.LpVariable(f"is_{s}_{v}", cat="Binary") for v in values}
                for s in names}
    for s in names:
        problem += pulp.lpSum(is_value[s].values()) == 1
    number = {s: pulp.lpSum(v * is_value[s][v] for v in values) for s in names}
    square = {s: pulp.lpSum(v * v * is_value[s][v] for v in values) for s in names}

    # every square holds a different number
    for v in values:
        problem += pulp.lpSum(is_value[s][v] for s in names) <= 1

    # the four numbers placed as examples stand as they are
    for s, v in given.items():
        problem += is_value[s][v] == 1

    # adjacent pairs and the pairs diametrically opposite them: A,B with F,G; B,C with
    # G,H; C,D with H,I; D,E with I,K; E,F with K,A
    for k in range(5):
        a, b = names[k], names[k + 1]
        c, d = names[k + 5], names[(k + 6) % 10]
        problem += square[a] + square[b] == square[c] + square[d]

    return problem, number

"""Frog circle: lay the cards 1..n face up at n positions around a circle. A frog starts on
card 1 at position 0 and repeatedly jumps clockwise as many positions as the card it sits on
shows. Arrange the cards so that the frog lands on every position exactly once in n - 1 jumps.

The model reports the card at each position.
"""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]  # number of cards and positions
    positions = range(n)
    steps = range(n)
    cards = range(1, n + 1)

    model = Model("frog_circle")

    # card_at[p, c] is 1 when card c lies at position p. Every position holds one card and every
    # card lies at one position, so the cards are all different.
    card_at = {(p, c): model.binary_var(name=f"card_at_{p}_{c}") for p in positions for c in cards}
    for p in positions:
        model.add_constraint(model.sum(card_at[p, c] for c in cards) == 1)
    for c in cards:
        model.add_constraint(model.sum(card_at[p, c] for p in positions) == 1)
    # x[p] is the card at position p.
    x = [model.sum(c * card_at[p, c] for c in cards) for p in positions]

    # visits[i, p] is 1 when the frog is at position p after i jumps. It is at one position at
    # each step and visits every position once, so the positions are all different.
    visits = {(i, p): model.binary_var(name=f"visits_{i}_{p}") for i in steps for p in positions}
    for i in steps:
        model.add_constraint(model.sum(visits[i, p] for p in positions) == 1)
    for p in positions:
        model.add_constraint(model.sum(visits[i, p] for i in steps) == 1)
    pos = [model.sum(p * visits[i, p] for p in positions) for i in steps]

    # visited[i] is the card the frog sits on after i jumps: the card at position pos[i]. One
    # indicator per step and position copies the card at the frog's position.
    visited = [model.integer_var(1, n, name=f"visited_{i}") for i in steps]
    for i in steps:
        for p in positions:
            model.add_indicator(visits[i, p], visited[i] == x[p])

    # The frog starts on card 1 at position 0.
    model.add_constraint(x[0] == 1)
    model.add_constraint(pos[0] == 0)
    model.add_constraint(visited[0] == 1)

    # The next position is the previous position plus the card there, modulo n. The sum is
    # below 2 * n, so wraps[i] (0 or 1) says whether the jump passes position 0.
    for i in range(1, n):
        wraps = model.binary_var(name=f"wraps_{i}")
        model.add_constraint(pos[i] == pos[i - 1] + visited[i - 1] - n * wraps)

    return model, {"x": x}

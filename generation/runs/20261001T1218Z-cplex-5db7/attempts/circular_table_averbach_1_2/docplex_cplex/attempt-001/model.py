"""Averbach 1.2: three players X, Y, Z of nationalities American, English and French sit
around a circular table and each passes three cards to the person on their right.

Seats are numbered 0, 1, 2 with seat 1 right of seat 0, seat 2 right of seat 1, and seat 0
right of seat 2. Each player and each nationality gets a seat; equal seats match a player to
their nationality.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data: three players, three nationalities, three seats.
    n = 3
    seats = range(n)

    model = Model("circular_table_averbach_1_2")

    def seat_variables(name):
        # at[i, s] is 1 when person i sits at seat s; each person has one seat and no two
        # people share a seat (all different).
        at = {(i, s): model.binary_var(name=f"{name}_{i}_{s}") for i in range(n) for s in seats}
        for i in range(n):
            model.add_constraint(model.sum(at[i, s] for s in seats) == 1)
        for s in seats:
            model.add_constraint(model.sum(at[i, s] for i in range(n)) == 1)
        return [model.sum(s * at[i, s] for s in seats) for i in range(n)]

    x, y, z = seat_variables("player")
    american, english, french = seat_variables("nationality")

    def right_to(a, b, name):
        # a is right of b: a == (b + 1) mod 3. With b in 0..2, b + 1 is 1..3, so
        # a == b + 1 - 3 * wrap, where wrap is 1 only when b + 1 == 3.
        wrap = model.binary_var(name=name)
        model.add_constraint(a == b + 1 - n * wrap)

    # Y passed three hearts to the American, so the American sits right of Y.
    right_to(american, y, "wrap_american")
    # X passed to the person who passed to the Frenchwoman, so X sits right of the Frenchwoman.
    right_to(x, french, "wrap_x")

    return model, {"x": x, "y": y, "z": z,
                   "american": american, "english": english, "french": french}

"""Circular table (Averbach 1.2): three players X, Y, Z of different nationalities (American,
English, French) sit around a table and each passes cards to the person on their right.
Y passed cards to the American, and X passed cards to the person who passed cards to the
Frenchwoman. Determine the nationality of each person.

The model reports the seat (0, 1 or 2) of each player and each nationality; seat s+1 mod 3
is to the right of seat s, and a player and a nationality with the same seat match.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data

    n = 3
    seats = range(n)
    players = ["x", "y", "z"]
    nationalities = ["american", "english", "french"]

    problem = pulp.LpProblem("circular_table_averbach_1_2", pulp.LpMinimize)  # satisfaction

    # at[name][s] = 1 if the player (or nationality) named has seat s; within each group
    # the seats are all different
    at = {name: {s: pulp.LpVariable(f"at_{name}_{s}", cat="Binary") for s in seats}
          for name in players + nationalities}
    for group in (players, nationalities):
        for name in group:
            problem += pulp.lpSum(at[name].values()) == 1
        for s in seats:
            problem += pulp.lpSum(at[name][s] for name in group) == 1

    # Y passed three hearts to the American: the American sits right of Y
    for s in seats:
        problem += at["american"][(s + 1) % n] == at["y"][s]

    # X passed cards to the person who passed cards to the Frenchwoman: X sits right of
    # the Frenchwoman
    for s in seats:
        problem += at["x"][(s + 1) % n] == at["french"][s]

    seat = {name: pulp.lpSum(s * at[name][s] for s in seats) for name in at}
    return problem, seat

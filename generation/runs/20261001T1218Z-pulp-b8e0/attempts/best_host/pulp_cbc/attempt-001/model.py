"""Best host: seat six guests around a round dinner table so that every guest sits only
next to the two guests they get along with.

The model reports the guests in seating order (Andrew 0, Betty 1, Cara 2, Dave 3,
Erica 4, Frank 5).
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its preferences are below

    n = 6
    Andrew, Betty, Cara, Dave, Erica, Frank = range(n)
    # the two guests each guest will sit next to, from the puzzle statement
    prefs = [
        [Dave, Frank],   # Andrew
        [Cara, Erica],   # Betty
        [Betty, Frank],  # Cara
        [Andrew, Erica],  # Dave
        [Betty, Dave],   # Erica
        [Andrew, Cara],  # Frank
    ]
    seats = range(n)
    guests = range(n)

    problem = pulp.LpProblem("best_host", pulp.LpMinimize)  # satisfaction

    # sit[i][g] = 1 if guest g sits in seat i; every guest has one seat and every seat
    # one guest, which is the all-different on the seating order
    sit = [[pulp.LpVariable(f"sit_{i}_{g}", cat="Binary") for g in guests] for i in seats]
    for i in seats:
        problem += pulp.lpSum(sit[i]) == 1
    for g in guests:
        problem += pulp.lpSum(sit[i][g] for i in seats) == 1

    # each guest sits only next to guests from their list: two guests who do not get
    # along never occupy neighbouring seats (the table is round, so seat n-1 is next to 0)
    for i in seats:
        j = (i + 1) % n
        for g in guests:
            for h in guests:
                if h != g and (h not in prefs[g] or g not in prefs[h]):
                    problem += sit[i][g] + sit[j][h] <= 1

    x = [pulp.lpSum(g * sit[i][g] for g in guests) for i in seats]
    return problem, {"x": x}

# Dinner party seating: seat six guests around a round table so that every pair of
# neighbouring guests is someone the guest is willing to sit next to.
# Guests are numbered 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank.
# The willing neighbours are problem data from the statement.
# s[g][p] is true when guest g sits in seat p; each seat is numbered 0..5 around the table.
from paramita.modelling import Bool

N = 6
WILLING = {  # guest -> guests they will sit next to (from the statement)
    0: {3, 5},  # Andrew: Dave, Frank
    1: {2, 4},  # Betty: Cara, Erica
    2: {1, 5},  # Cara: Betty, Frank
    3: {0, 4},  # Dave: Andrew, Erica
    4: {1, 3},  # Erica: Betty, Dave
    5: {0, 2},  # Frank: Andrew, Cara
}


def build(instance):
    s = [[Bool(f"seat_{g}_{p}") for p in range(N)] for g in range(N)]
    cons = []

    # each guest sits in exactly one seat
    for g in range(N):
        cons.append(sum(s[g]) == 1)

    # each seat holds exactly one guest
    for p in range(N):
        cons.append(sum(s[g][p] for g in range(N)) == 1)

    # the table is round: seat 5 is next to seat 0
    # two guests who will not sit next to each other are never in neighbouring seats
    for p in range(N):
        q = (p + 1) % N
        for g in range(N):
            for h in range(N):
                if g != h and h not in WILLING[g]:
                    cons.append(~(s[g][p] & s[h][q]))

    # the guest in each seat, in seating order
    outputs = {"x": [sum(g * s[g][p] for g in range(N)) for p in range(N)]}
    return cons, outputs

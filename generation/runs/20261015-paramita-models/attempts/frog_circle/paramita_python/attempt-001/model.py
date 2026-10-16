# Frog circle: cards 1..n are arranged on a circle and a frog jumps around it.
# The frog starts on card 1, then from card k jumps k places clockwise,
# and must land on every card exactly once in n jumps.
# Output x[p] is the card number at position p (0-based, clockwise).
from paramita.modelling import Bool, If


def build(instance):
    n = instance["n"]
    cards = range(1, n + 1)

    # xv[p][v] = card v sits at position p
    xv = [{v: Bool(f"x_{p}_{v}") for v in cards} for p in range(n)]
    # y[i][p] = the frog stands on position p at jump i (i = 0 .. n-1)
    y = [[Bool(f"y_{i}_{p}") for p in range(n)] for i in range(n)]

    cons = []

    # every position holds exactly one card
    cons += [sum(xv[p].values()) == 1 for p in range(n)]
    # every card is at exactly one position
    cons += [sum(xv[p][v] for p in range(n)) == 1 for v in cards]

    # the frog starts on card 1, which is at position 0
    cons.append(xv[0][1])
    cons.append(y[0][0])

    # the frog is on exactly one position at each jump
    cons += [sum(y[i]) == 1 for i in range(n)]
    # every position is visited exactly once, so every card is jumped on once
    cons += [sum(y[i][p] for i in range(n)) == 1 for p in range(n)]

    # from card v at position p, the frog jumps v places clockwise to (p + v) mod n
    for i in range(n - 1):
        for p in range(n):
            for v in cards:
                q = (p + v) % n
                cons.append(If(y[i][p] & xv[p][v], y[i + 1][q]))

    x = [sum(v * xv[p][v] for v in cards) for p in range(n)]
    return cons, {"x": x}

"""Circling the squares: place a different whole number in each of the ten squares A, B, C, D, E, F, G, H, I, K
around a circle, so that the squares of any two adjacent numbers sum to the squares of the two numbers opposite them."""
from paramita.modelling import Bool, If

# The ten squares in circle order. Square i is adjacent to i-1 and i+1, and opposite to i+5.
SQUARES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]
LO, HI = 0, 99  # fractions are not allowed and no number needs more than two figures
SQ_BITS = 14  # 99 * 99 = 9801 < 2**14


def build(instance):
    cons = []

    # one-hot integer per square: xv[p][v] is true when square p holds the number v
    xv = {p: {v: Bool(f"{p}_is_{v}") for v in range(LO, HI + 1)} for p in SQUARES}
    value = {p: sum(v * xv[p][v] for v in range(LO, HI + 1)) for p in SQUARES}

    # each square holds exactly one number
    for p in SQUARES:
        cons.append(sum(xv[p].values()) == 1)

    # a different number in each of the ten squares: no number is used twice
    for v in range(LO, HI + 1):
        cons.append(sum(xv[p][v] for p in SQUARES) <= 1)

    # the four numbers placed as examples must stand as they are: A=16, B=2, F=8, G=14
    cons.append(value["A"] == 16)
    cons.append(value["B"] == 2)
    cons.append(value["F"] == 8)
    cons.append(value["G"] == 14)

    # the square of each square's number, in binary: sqb[p] holds the bits of v*v when p holds v
    # (binary keeps the weights small; a weighted sum of v*v over the one-hot is too hard to encode)
    sq = {}
    for p in SQUARES:
        bits = [Bool(f"{p}_square_bit_{k}") for k in range(SQ_BITS)]
        for v in range(LO, HI + 1):
            for k in range(SQ_BITS):
                cons.append(If(xv[p][v], bits[k] if (v * v >> k) & 1 else ~bits[k]))
        sq[p] = sum((2 ** k) * bits[k] for k in range(SQ_BITS))

    # for any two adjacent squares, the sum of their squares equals the sum of the squares
    # of the two squares diametrically opposite them (edge i, i+1 against edge i+5, i+6);
    # the equation for edge i+5 is the same as for edge i, so i = 0..4 covers all of them
    for i in range(5):
        a, b = SQUARES[i], SQUARES[(i + 1) % 10]
        c, d = SQUARES[(i + 5) % 10], SQUARES[(i + 6) % 10]
        cons.append(sq[a] + sq[b] == sq[c] + sq[d])

    outputs = {p: value[p] for p in SQUARES}
    return cons, outputs

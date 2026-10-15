from paramita.modelling import Bool

# Hanging weights: thirteen weights A-M hang from a system of bars. Each
# weight is an integer between 1 and 13. The weights on either side of a
# pivot balance when weighted by their distance from the pivot, and a bar
# hanging beneath another contributes its total weight as one weight.

LETTERS = "abcdefghijklm"
LO, HI = 1, 13


def build(instance):
    cons = []

    # Each weight is an integer 1..13: one-hot Bools, exactly one is true.
    val = {}
    for n in LETTERS:
        bits = {v: Bool(f"w_{n}_{v}") for v in range(LO, HI + 1)}
        cons.append(sum(bits.values()) == 1)
        val[n] = sum(v * b for v, b in bits.items())

    A, B, C, D, E, F, G = (val[x] for x in "abcdefg")
    H, I, J, K, L, M = (val[x] for x in "hijklm")

    # Subtree weights: a bar hanging beneath another contributes its total weight.
    W5 = E + F          # bar holding E and F
    W3 = H + I + W5     # bar holding H and I, and the E-F bar beneath it
    W2 = W3 + L + M     # bar holding L and M, and the H-I bar beneath it
    X = A + B           # bar holding A and B
    Y = C + D           # bar holding C and D
    W6 = G + Y          # bar holding G, and the C-D bar beneath it
    W4 = X + J + K + W6 # bar holding J and K, and the A-B and G bars beneath it

    # Top bar, hung at the stem: the L-M bar at distance 12 left, the J-K bar at distance 9 right.
    cons.append(12 * W2 == 9 * W4)

    # Bar holding L and M, hung from the top bar: the H-I bar at distance 3 left,
    # L at distance 3 right, M at distance 12 right.
    cons.append(3 * W3 == 3 * L + 12 * M)

    # Bar holding H and I, hung at column 9: H at distance 9 left, the E-F bar at
    # distance 6 right, I at distance 9 right.
    cons.append(9 * H == 6 * W5 + 9 * I)

    # Bar holding E and F: E at distance 9 left, F at distance 6 right.
    cons.append(9 * E == 6 * F)

    # Bar holding J and K: the A-B bar at distance 8 left, J at distance 5 left,
    # K at distance 4 right, the G bar at distance 7 right.
    cons.append(8 * X + 5 * J == 4 * K + 7 * W6)

    # Bar holding A and B: A at distance 12 left, B at distance 3 right.
    cons.append(12 * A == 3 * B)

    # Bar holding G, hung from the J-K bar: G at distance 9 left, the C-D bar
    # at distance 6 right. Description: 3*G = 2*(C+D).
    cons.append(9 * G == 6 * Y)

    # Bar holding C and D: C at distance 15 left, D at distance 3 right.
    # Description: 5*C = D.
    cons.append(15 * C == 3 * D)

    outputs = {n: val[n] for n in LETTERS}
    return cons, outputs

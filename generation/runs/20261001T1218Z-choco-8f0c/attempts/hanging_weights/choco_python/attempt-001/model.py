# Hanging weights: thirteen different weights A..M, each 1..13, hang from a system of bars; find
# the weights that balance every bar (weight times distance equal on both sides of each pivot, a
# hanging bar counting as one weight equal to its total).
from pychoco.model import Model

# The puzzle has no instance data; the bar layout (the balance equations below) is its statement.
N = 13


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    names = "abcdefghijklm"
    w = {name: model.intvar(1, N, name=name) for name in names}
    a, b, c, d, e, f, g, h, i, j, k, l, m = (w[x] for x in names)

    def balance(left, right):
        """sum of coefficient * weight on the left equals that on the right"""
        vs = [v for _, v in left] + [v for _, v in right]
        cs = [q for q, _ in left] + [-q for q, _ in right]
        model.scalar(vs, cs, "=", 0).post()

    # Every weight is different.
    model.all_different(list(w.values())).post()

    # Bottom left bar (A and B): 4A = B.
    balance([(4, a)], [(1, b)])
    # Bottom right bar (C and D): 5C = D.
    balance([(5, c)], [(1, d)])
    # Bar holding E and F: 3E = 2F.
    balance([(3, e)], [(2, f)])
    # Bar holding G and the C-D bar: 3G = 2(C + D).
    balance([(3, g)], [(2, c), (2, d)])
    # Bar holding the A-B bar, J, K and the G bar: 3(A + B) + 2J = K + 2(G + C + D).
    balance([(3, a), (3, b), (2, j)], [(1, k), (2, g), (2, c), (2, d)])
    # Bar holding H, I and the E-F bar: 3H = 2(E + F) + 3I.
    balance([(3, h)], [(2, e), (2, f), (3, i)])
    # Bar holding the H bar, L and M: H + I + E + F = L + 4M.
    balance([(1, h), (1, i), (1, e), (1, f)], [(1, l), (4, m)])
    # Top bar: 4(L + M + H + I + E + F) = 3(J + K + G + A + B + C + D).
    balance([(4, l), (4, m), (4, h), (4, i), (4, e), (4, f)],
            [(3, j), (3, k), (3, g), (3, a), (3, b), (3, c), (3, d)])

    return model, w

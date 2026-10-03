# Circling the squares (Dudeney): place ten different numbers A..K round a circle so that for any
# two adjacent numbers, the sum of their squares equals the sum of the squares of the two numbers
# diametrically opposite. A=16, B=2, F=8 and G=14 are given.
from pychoco.model import Model

# The puzzle has no instance data. The four given numbers are its statement, and "no number need
# contain more than two figures" bounds every number by 1..99.
N = 10
GIVEN = {"A": 16, "B": 2, "F": 8, "G": 14}
NAMES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # x[k] = the number in square NAMES[k], going round the circle
    x = [model.intvar(1, 99, name=name) for name in NAMES]
    # sq[k] = the square of x[k]
    sq = [model.intvar(1, 99 * 99, name=f"sq_{name}") for name in NAMES]
    for v, s in zip(x, sq):
        model.square(s, v).post()

    # Every square holds a different number.
    model.all_different(x).post()

    # The four numbers placed as examples stay as they are.
    for name, value in GIVEN.items():
        model.arithm(x[NAMES.index(name)], "=", value).post()

    # Adjacent pair k, k+1 and the diametrically opposite pair k+5, k+6 have equal sums of
    # squares: A,B with F,G; B,C with G,H; C,D with H,I; D,E with I,K; E,F with K,A.
    half = N // 2
    for k in range(half):
        p, q = k, k + 1
        r, s = (k + half) % N, (k + half + 1) % N
        model.scalar([sq[p], sq[q], sq[r], sq[s]], [1, 1, -1, -1], "=", 0).post()

    return model, {name: v for name, v in zip(NAMES, x)}

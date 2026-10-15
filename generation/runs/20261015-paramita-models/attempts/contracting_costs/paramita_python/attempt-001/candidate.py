from paramita.modelling import Bool

# Contracting costs: a contractor pays pairs of workers known amounts.
# Each worker's charge is a nonnegative integer written in 13 binary bits
# (2^13 - 1 = 8191 >= 5300, the largest payment), so the charge is a PB sum.
# The six payments form a linear system with one solution (see plan.md).

BITS = 13
NAMES = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]


def charge_bits(name):
    return [Bool(f"{name}_bit_{k}") for k in range(BITS)]


def value(bits):
    return sum((2**k) * b for k, b in enumerate(bits))


def build(instance):
    bits = {name: charge_bits(name) for name in NAMES}
    ph = value(bits["paper_hanger"])
    pp = value(bits["painter"])
    pl = value(bits["plumber"])
    el = value(bits["electrician"])
    ca = value(bits["carpenter"])
    ma = value(bits["mason"])

    cons = []
    # $1,100 to the paper hanger and the painter
    cons.append(ph + pp == 1100)
    # $1,700 to the painter and plumber
    cons.append(pp + pl == 1700)
    # $1,100 to the plumber and electrician
    cons.append(pl + el == 1100)
    # $3,300 to the electrician and carpenter
    cons.append(el + ca == 3300)
    # $5,300 to the carpenter and mason
    cons.append(ca + ma == 5300)
    # $3,200 to the mason and painter
    cons.append(ma + pp == 3200)

    outputs = {
        "paper_hanger": ph,
        "painter": pp,
        "plumber": pl,
        "electrician": el,
        "carpenter": ca,
        "mason": ma,
    }
    return cons, outputs

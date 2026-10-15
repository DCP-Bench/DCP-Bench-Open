# Birthday coins puzzle (old British currency).
# Each coin count is a one-hot integer over 0..15: count_v[v] is true when the count is v.
# Pence values: half-crown 30, shilling 12, sixpence 6. A pound is 240 pence, so 1 pound 5 shillings 6 pence is 306 pence.
from paramita.modelling import Bool

TOTAL_COINS = 15        # from the problem statement
TOTAL_PENCE = 306       # 1 pound 5 shillings 6 pence, from the problem statement
MAX_COUNT = TOTAL_COINS # a count cannot exceed the number of coins


def one_hot(name):
    return {v: Bool(f"{name}_is_{v}") for v in range(MAX_COUNT + 1)}


def value(bits):
    return sum(v * b for v, b in bits.items())


def build(instance):
    # instance has no fields for this problem; the numbers come from the statement above
    half_crown = one_hot("half_crowns")
    shilling = one_hot("shillings")
    sixpence = one_hot("sixpence")

    h = value(half_crown)
    s = value(shilling)
    k = value(sixpence)

    cons = []

    # each count takes exactly one value
    cons += [sum(half_crown.values()) == 1, sum(shilling.values()) == 1, sum(sixpence.values()) == 1]

    # he was given 15 coins
    cons += [h + s + k == TOTAL_COINS]

    # the coins add up to 1 pound 5 shillings 6 pence (306 pence)
    cons += [30 * h + 12 * s + 6 * k == TOTAL_PENCE]

    # each kind of coin is among the coins given
    cons += [h >= 1, s >= 1, k >= 1]

    return cons, {"half_crowns": h}

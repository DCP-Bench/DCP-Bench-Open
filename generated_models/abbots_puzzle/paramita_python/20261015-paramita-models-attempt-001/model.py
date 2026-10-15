# Abbot's puzzle: 100 bushels of corn are distributed among 100 people (men,
# women, children) so that each man gets three bushels, each woman two and each
# child half a bushel, and there are five times as many women as men.
# Find the number of men, women and children.
#
# Integers are one-hot encoded: Bool "men_v" is true when there are v men.
# Bushels are counted in half-bushels, so that each child's share is an integer.
#
# The totals (100 bushels, 100 people, 5 women per man) are problem constants
# from the statement, not instance fields; the instance carries no data.
from paramita.modelling import Bool

BUSHELS = 100          # the corn to distribute, in bushels
PEOPLE = 100           # the number of people who share it
MAX_COUNT = PEOPLE     # a count of people cannot exceed the number of people


def one_hot(name):
    # one Bool per possible count 0..MAX_COUNT, exactly one of them true
    return {v: Bool(f"{name}_{v}") for v in range(MAX_COUNT + 1)}


def count_expr(oh, scale=1):
    # the integer value of a one-hot count, multiplied by scale
    return sum(scale * v * oh[v] for v in range(1, MAX_COUNT + 1))


def build(instance):
    men_oh = one_hot("men")
    women_oh = one_hot("women")
    children_oh = one_hot("children")

    cons = []
    # each of men, women and children takes exactly one count
    cons += [sum(men_oh.values()) == 1,
             sum(women_oh.values()) == 1,
             sum(children_oh.values()) == 1]

    # the 100 people are the men, the women and the children
    cons += [count_expr(men_oh) + count_expr(women_oh) + count_expr(children_oh) == PEOPLE]

    # each man received three bushels (6 half-bushels), each woman two (4 half-bushels),
    # each child half a bushel (1 half-bushel): the total is 100 bushels (200 half-bushels)
    cons += [count_expr(men_oh, 6) + count_expr(women_oh, 4) + count_expr(children_oh, 1)
             == 2 * BUSHELS]

    # there are five times as many women as men
    cons += [count_expr(women_oh) == count_expr(men_oh, 5)]

    outputs = {
        "children": count_expr(children_oh),
        "men": count_expr(men_oh),
        "women": count_expr(women_oh),
    }
    return cons, outputs

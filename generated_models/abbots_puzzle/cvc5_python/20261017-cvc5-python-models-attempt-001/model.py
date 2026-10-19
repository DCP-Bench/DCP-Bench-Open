# Abbot's puzzle: 100 bushels of corn are distributed among 100 people.
# Each man receives three bushels, each woman two, each child half a bushel.
# There are five times as many women as men.
# Find the number of men, women and children.
import cvc5.pythonic as cz


def build(instance):
    men, women, children = cz.Ints("men women children")

    # Counts are non-negative integers.
    bounds = [men >= 0, women >= 0, children >= 0]

    # Every one of the 100 people is a man, a woman or a child.
    # The number of people is fixed by the description, not by the data.
    people = [men + women + children == 100]

    # The 100 bushels are distributed: men get 3, women 2, children 1/2 each.
    # Multiplied by 2 to keep the arithmetic in integers.
    corn = [6 * men + 4 * women + children == 200]

    # There are five times as many women as men.
    ratio = [women == 5 * men]

    return bounds + people + corn + ratio, {"men": men, "women": women, "children": children}

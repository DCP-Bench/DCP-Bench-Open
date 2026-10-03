# Abbot's puzzle: 100 bushels of corn are shared among 100 people. Each man gets three
# bushels, each woman two and each child half a bushel, and there are five times as many
# women as men. Find the number of men, women and children.
from hermax.model import Model


def build(instance):
    # This puzzle has no instance data: the 100 people, the 100 bushels and the factor of
    # five are part of the problem itself, so they are written here as constants.
    m = Model()
    # men, women, children = number of people of each kind (at most 100 people in all)
    men = m.int("men", 0, 100)
    women = m.int("women", 0, 100)
    children = m.int("children", 0, 100)

    # the 100 people are men, women and children
    m &= (men + women + children == 100)
    # The 100 bushels are shared out: 3 per man, 2 per woman, 1/2 per child. Written in
    # half bushels, as the reference does, so that every number is an integer:
    # 6 per man, 4 per woman, 1 per child, 200 in all.
    m &= (men * 6 + women * 4 + children == 200)
    # there are five times as many women as men
    m &= (men * 5 == women)

    return m, {"men": men, "women": women, "children": children}

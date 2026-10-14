# Dinner: take 1-6 grandparents ($3 each), 1-10 parents ($2 each) and 1-40 children
# ($0.50 each) out to dinner, 20 people in all for $20. How many of each go?
from hermax.model import Model


def build(instance):
    # The prices, ranges and totals are fixed by the problem; the instance carries no data.
    m = Model()
    # "1-6 grandparents, 1-10 parents and/or 1-40 children"
    grandparents = m.int("grandparents", 1, 6)
    parents = m.int("parents", 1, 10)
    children = m.int("children", 1, 40)

    # it must cost $20: $3, $2 and $0.50 a head, doubled to avoid the half dollar
    m &= (6 * grandparents + 4 * parents + children == 20 * 2)
    # there must be 20 people at dinner
    m &= (grandparents + parents + children == 20)

    return m, {"grandparents": grandparents, "parents": parents, "children": children}

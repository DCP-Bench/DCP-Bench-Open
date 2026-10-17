# Dinner problem: how many grandparents, parents and children go to dinner.
# Taking 1-6 grandparents, 1-10 parents and/or 1-40 children; grandparents cost $3,
# parents $2 and children $0.50; there must be 20 total people and it must cost $20.
import cvc5.pythonic as cz


def build(instance):
    grandparents, parents, children = cz.Ints("grandparents parents children")

    # We're going out to dinner taking 1-6 grandparents, 1-10 parents and/or 1-40 children
    ranges = [
        grandparents >= 1, grandparents <= 6,
        parents >= 1, parents <= 10,
        children >= 1, children <= 40,
    ]

    # There must be 20 total people at dinner
    total_people = [grandparents + parents + children == 20]

    # and it must cost $20 (costs in cents: 300, 200 and 50 per person)
    total_cost = [300 * grandparents + 200 * parents + 50 * children == 2000]

    constraints = ranges + total_people + total_cost
    outputs = {
        "grandparents": grandparents,
        "parents": parents,
        "children": children,
    }
    return constraints, outputs

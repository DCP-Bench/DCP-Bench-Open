# Contracting costs (Sam Loyd): from what the contractor pays six pairs of
# tradesmen together, find what each of the six charges.
import z3


def build(instance):
    del instance  # the puzzle states its own payments

    paper_hanger, painter, plumber, electrician, carpenter, mason = people = z3.Ints(
        "paper_hanger painter plumber electrician carpenter mason")

    # Problem data: (first person, second person, what the pair costs together).
    pair_costs = [
        (paper_hanger, painter, 1100),
        (painter, plumber, 1700),
        (plumber, electrician, 1100),
        (electrician, carpenter, 3300),
        (carpenter, mason, 5300),
        (mason, painter, 3200),
    ]

    solver = z3.Solver()

    # Each charge is a positive amount, and no charge can exceed the largest payment.
    largest = max(cost for _, _, cost in pair_costs)
    for p in people:
        solver.add(p >= 1, p <= largest)

    # What the contractor pays the two members of each pair adds up to the stated total.
    for first, second, cost in pair_costs:
        solver.add(first + second == cost)

    return solver, {
        "paper_hanger": paper_hanger, "painter": painter, "plumber": plumber,
        "electrician": electrician, "carpenter": carpenter, "mason": mason,
    }

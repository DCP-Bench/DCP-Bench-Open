# Contracting costs: a contractor pays pairs of workers a fixed sum per pair of
# trades, and we must find what each man charges for his services.
import cvc5.pythonic as cz


def build(instance):
    paper_hanger, painter, plumber, electrician, carpenter, mason = cz.Ints(
        "paper_hanger painter plumber electrician carpenter mason"
    )
    constraints = [
        # Charges are non-negative dollar amounts.
        paper_hanger >= 0,
        painter >= 0,
        plumber >= 0,
        electrician >= 0,
        carpenter >= 0,
        mason >= 0,
    ]
    # $ 1,100 to the paper hanger and the painter,
    # $ 1,700 to the painter and plumber,
    # $ 1,100 to the plumber and electrician,
    # $ 3,300 to the electrician and carpenter,
    # $ 5,300 to the carpenter and mason,
    # $ 3,200 to the mason and painter.
    constraints += [
        paper_hanger + painter == 1100,
        painter + plumber == 1700,
        plumber + electrician == 1100,
        electrician + carpenter == 3300,
        carpenter + mason == 5300,
        mason + painter == 3200,
    ]
    outputs = {
        "paper_hanger": paper_hanger,
        "painter": painter,
        "plumber": plumber,
        "electrician": electrician,
        "carpenter": carpenter,
        "mason": mason,
    }
    return constraints, outputs

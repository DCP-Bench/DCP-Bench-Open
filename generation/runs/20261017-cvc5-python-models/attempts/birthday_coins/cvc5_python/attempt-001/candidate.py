# birthday_coins: Tommy was given 15 coins (half-crowns, shillings and sixpence) that add
# up to 1 pound 5 shillings 6 pence. Print the number of half-crowns he was given.
import cvc5.pythonic as cz


def build(instance):
    half_crowns, shillings, sixpences = cz.Ints("half_crowns shillings sixpences")

    constraints = []

    # Tommy was given 15 coins in total.
    constraints.append(half_crowns + shillings + sixpences == 15)

    # He was given half-crowns, shillings and sixpence, so each kind is present.
    constraints.append(half_crowns >= 1)
    constraints.append(shillings >= 1)
    constraints.append(sixpences >= 1)

    # The coins add up to 1 pound 5 shillings 6 pence, which is 306 pence:
    # a half-crown is 30 pence, a shilling 12 pence and a sixpence 6 pence.
    constraints.append(30 * half_crowns + 12 * shillings + 6 * sixpences == 306)

    return constraints, {"half_crowns": half_crowns}

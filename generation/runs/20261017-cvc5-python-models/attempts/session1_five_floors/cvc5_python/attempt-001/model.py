# Five floors puzzle (session1_five_floors): Baker, Cooper, Fletcher, Miller and Smith
# live on floors 1 to 5 of an apartment house, one person per floor.
import cvc5.pythonic as cz


def build(instance):
    B, C, F, M, S = cz.Ints("B C F M S")
    people = [B, C, F, M, S]

    # They all live on different floors, on the first five floors.
    constraints = [cz.Distinct(people)]
    for p in people:
        constraints += [p >= 1, p <= 5]

    # Baker does not live on the fifth floor.
    # Cooper does not live on the first floor.
    # Fletcher does not live on either the fifth or the first floor.
    constraints += [B != 5, C != 1, F != 5, F != 1]

    # Miller lives on a higher floor than does Cooper.
    constraints += [M > C]

    # Smith does not live on a floor adjacent to Fletcher's.
    constraints += [cz.Or(S - F >= 2, F - S >= 2)]

    # Fletcher does not live on a floor adjacent to Cooper's.
    constraints += [cz.Or(F - C >= 2, C - F >= 2)]

    return constraints, {"B": B, "C": C, "F": F, "M": M, "S": S}

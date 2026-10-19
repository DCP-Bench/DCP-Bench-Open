# Circular table (Averbach 1.2): three players X, Y, Z of nationalities American, English and
# French sit around a circular table. Seats are 0, 1, 2, and seat 1 is right of seat 0, seat 2
# is right of seat 1, and so on around the table.
import cvc5.pythonic as cz


def right(p):
    # The person on the right of seat p.
    return cz.If(p == 2, 0, p + 1)


def build(instance):
    x, y, z = cz.Ints("x y z")
    american, english, french = cz.Ints("american english french")
    seats = [x, y, z, american, english, french]

    # Three players and three nationalities, each taking a seat in 0..2.
    # The same value denotes the matching between a person and a nationality.
    domain = [cz.And(v >= 0, v <= 2) for v in seats]
    players_distinct = cz.Distinct([x, y, z])
    nationalities_distinct = cz.Distinct([american, english, french])

    # Each passed three cards to the person on their right.
    # Y passed three hearts to the American.
    passed_hearts = american == right(y)

    # X passed the queen of spades and two diamonds to the person who passed their cards
    # to the Frenchwoman: X passed to person q, and q passed to the Frenchwoman.
    passed_to_french = french == right(right(x))

    constraints = domain + [players_distinct, nationalities_distinct, passed_hearts, passed_to_french]
    outputs = {
        "x": x,
        "y": y,
        "z": z,
        "american": american,
        "english": english,
        "french": french,
    }
    return constraints, outputs

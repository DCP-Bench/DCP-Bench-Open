# Crew assignment: staff each flight with cabin crew from a pool of flight
# attendants. A flight needs a given number of crew, of whom certain numbers
# must be stewards, hostesses and speakers of French, Spanish and German, and
# an attendant must have the two flights after an attended flight off.
from hermax.model import Model


def build(instance):
    attributes = instance["attributes"]  # per person: steward, hostess, French, Spanish, German (0/1)
    required = instance["required_crew"]  # per flight: crew size, then the minimum count for each attribute
    n_persons = len(attributes)
    n_flights = len(required)
    n_attributes = len(attributes[0])

    m = Model()
    # crew[f][p] is true when person p works on flight f
    crew = m.bool_matrix("crew", n_flights, n_persons)

    for f in range(n_flights):
        # the flight has exactly the number of crew members it needs
        m &= (sum(1 * crew[f][p] for p in range(n_persons)) == required[f][0])
        # and at least the required number of people with each attribute
        for a in range(n_attributes):
            skilled = [p for p in range(n_persons) if attributes[p][a]]
            m &= (sum(1 * crew[f][p] for p in skilled) >= required[f][a + 1])

    # after a flight a person has the next two flights off: no two of any three
    # consecutive flights are worked by the same person
    for f in range(n_flights - 2):
        for p in range(n_persons):
            m &= (~crew[f][p] | ~crew[f + 1][p])
            m &= (~crew[f][p] | ~crew[f + 2][p])
            m &= (~crew[f + 1][p] | ~crew[f + 2][p])

    return m, {"crew": crew}

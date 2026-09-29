# Crew assignment: staff each flight with cabin crew from a pool of flight
# attendants. A flight needs a given number of crew, of whom certain numbers
# must be stewards, hostesses and speakers of French, Spanish and German, and
# an attendant must have the two flights after an attended flight off.
from pychoco.model import Model


def build(instance):
    attributes = instance["attributes"]  # per person: steward, hostess, French, Spanish, German (0/1)
    required = instance["required_crew"]  # per flight: crew size, then the minimum count for each attribute
    n_persons = len(attributes)
    n_flights = len(required)
    n_attributes = len(attributes[0])

    model = Model()

    # crew[f][p] is true when person p works on flight f
    crew = [[model.boolvar(name=f"crew_{f}_{p}") for p in range(n_persons)] for f in range(n_flights)]

    for f in range(n_flights):
        # the flight has exactly the number of crew members it needs
        model.sum(crew[f], "=", required[f][0]).post()
        # and at least the required number of people with each attribute
        for a in range(n_attributes):
            model.scalar(crew[f], [attributes[p][a] for p in range(n_persons)], ">=", required[f][a + 1]).post()

    # after a flight a person has the next two flights off: at most one flight in any three in a row
    for f in range(n_flights - 2):
        for p in range(n_persons):
            model.sum([crew[f][p], crew[f + 1][p], crew[f + 2][p]], "<=", 1).post()

    return model, {"crew": crew}

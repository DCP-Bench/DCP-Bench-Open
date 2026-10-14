# Crew assignment: staff each flight with cabin crew from a pool of flight
# attendants. A flight needs a given number of crew, of whom certain numbers
# must be stewards, hostesses and speakers of French, Spanish and German, and
# an attendant must have the two flights after an attended flight off.
from exact import Exact


def build(instance):
    attributes = instance["attributes"]  # per person: steward, hostess, French, Spanish, German (0/1)
    required = instance["required_crew"]  # per flight: crew size, then the minimum count for each attribute
    n_persons = len(attributes)
    n_flights = len(required)
    n_attributes = len(attributes[0])

    solver = Exact()
    # crew[f][p] is 1 when person p works on flight f
    crew = [[f"crew_{f}_{p}" for p in range(n_persons)] for f in range(n_flights)]
    for row in crew:
        for name in row:
            solver.addVariable(name, 0, 1)

    for f in range(n_flights):
        # the flight has exactly the number of crew members it needs
        solver.addConstraint([(1, name) for name in crew[f]], True, required[f][0], True, required[f][0])
        # and at least the required number of people with each attribute
        for a in range(n_attributes):
            skilled = [(1, crew[f][p]) for p in range(n_persons) if attributes[p][a]]
            solver.addConstraint(skilled, True, required[f][a + 1])

    # after a flight a person has the next two flights off: at most one flight in any three in a row
    for f in range(n_flights - 2):
        for p in range(n_persons):
            solver.addConstraint([(1, crew[f][p]), (1, crew[f + 1][p]), (1, crew[f + 2][p])], False, 0, True, 1)

    return solver, {"crew": crew}

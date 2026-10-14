# Crew assignment: staff each flight with cabin crew from a pool of flight
# attendants. A flight needs a given number of crew, of whom certain numbers
# must be stewards, hostesses and speakers of French, Spanish and German, and
# an attendant must have the two flights after an attended flight off.
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def build(instance):
    attributes = instance["attributes"]  # per person: steward, hostess, French, Spanish, German (0/1)
    required = instance["required_crew"]  # per flight: crew size, then the minimum count for each attribute
    n_persons = len(attributes)
    n_flights = len(required)
    n_attributes = len(attributes[0])

    pool = IDPool()
    # crew[f][p] is true when person p works on flight f
    crew = [[pool.id(("crew", f, p)) for p in range(n_persons)] for f in range(n_flights)]

    cnf = CNF()
    for f in range(n_flights):
        # the flight has exactly the number of crew members it needs
        cnf.extend(CardEnc.equals(lits=crew[f], bound=required[f][0], vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
        # and at least the required number of people with each attribute
        for a in range(n_attributes):
            skilled = [crew[f][p] for p in range(n_persons) if attributes[p][a]]
            if required[f][a + 1] > 0:
                cnf.extend(CardEnc.atleast(lits=skilled, bound=required[f][a + 1], vpool=pool,
                                           encoding=EncType.seqcounter).clauses)

    # after a flight a person has the next two flights off: no two of any three
    # consecutive flights are worked by the same person
    for f in range(n_flights - 2):
        for p in range(n_persons):
            cnf.append([-crew[f][p], -crew[f + 1][p]])
            cnf.append([-crew[f][p], -crew[f + 2][p]])
            cnf.append([-crew[f + 1][p], -crew[f + 2][p]])

    return cnf, {"crew": crew}

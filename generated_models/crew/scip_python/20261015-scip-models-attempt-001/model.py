# Crew assignment: assign flight attendants to flights so that every flight has its
# required number of cabin crew and enough speakers of each language, and no attendant
# works a flight within two flights after an attended flight.
from pyscipopt import Model, quicksum


def build(instance):
    attributes = instance["attributes"]  # attributes[p][l] = 1 if attendant p speaks language l
    required = instance["required_crew"]  # required[f][0] = crew size; required[f][1 + l] = speakers of language l needed
    n_people = len(attributes)
    n_flights = len(required)
    n_langs = len(attributes[0])

    m = Model()
    # x[f, p] = 1 if attendant p is assigned to flight f
    x = {(f, p): m.addVar(name=f"x_{f}_{p}", vtype="B")
         for f in range(n_flights) for p in range(n_people)}

    for f in range(n_flights):
        # each flight needs exactly the required number of cabin crew
        m.addCons(quicksum(x[f, p] for p in range(n_people)) == required[f][0])
        # each language must be spoken by at least the required number of crew on the flight
        for l in range(n_langs):
            m.addCons(quicksum(attributes[p][l] * x[f, p] for p in range(n_people))
                      >= required[f][1 + l])

    # every crew member has the two flights after an attended flight off
    for p in range(n_people):
        for f in range(n_flights):
            for g in (f + 1, f + 2):
                if g < n_flights:
                    m.addCons(x[f, p] + x[g, p] <= 1)

    outputs = {"crew": [[x[f, p] for p in range(n_people)] for f in range(n_flights)]}
    return m, outputs

# Crew assignment: assign flight attendants to flights. Each flight needs a certain
# number of cabin crew, and they have to speak certain languages. Every cabin crew
# member has two flights off after an attended flight.
# crew[f][p] is True if person p is assigned to flight f.
# attributes[p] = [steward, hostess, French, Spanish, German] for person p.
# required_crew[f] = [total crew, stewards, hostesses, French, Spanish, German] for flight f.

import cvc5.pythonic as cz


def build(instance):
    attributes = instance["attributes"]
    required_crew = instance["required_crew"]

    n_people = len(attributes)
    n_flights = len(required_crew)
    n_attrs = len(attributes[0])

    # crew[f][p] is True when person p works flight f.
    crew = [[cz.Bool(f"crew_{f}_{p}") for p in range(n_people)] for f in range(n_flights)]
    constraints = []

    # Each flight has exactly its required number of crew members.
    for f in range(n_flights):
        constraints.append(
            cz.Sum([cz.If(crew[f][p], 1, 0) for p in range(n_people)]) == required_crew[f][0]
        )

    # Each flight has at least the required number of stewards, hostesses and speakers
    # of each language, counted over the crew assigned to it.
    for f in range(n_flights):
        for a in range(n_attrs):
            holders = [crew[f][p] for p in range(n_people) if attributes[p][a] == 1]
            if not holders:
                continue
            constraints.append(
                cz.Sum([cz.If(h, 1, 0) for h in holders]) >= required_crew[f][a + 1]
            )

    # Every cabin crew member has two flights off after an attended flight: a person who
    # works flight f does not work flight f+1 or f+2.
    for p in range(n_people):
        for f in range(n_flights):
            for g in (f + 1, f + 2):
                if g < n_flights:
                    constraints.append(cz.Not(cz.And(crew[f][p], crew[g][p])))

    outputs = {"crew": crew}
    return constraints, outputs

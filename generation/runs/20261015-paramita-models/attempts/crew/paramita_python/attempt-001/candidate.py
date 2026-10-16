# Crew assignment: 20 flight attendants on 10 flights.
# Each flight needs a crew size, a minimum number of stewards and hostesses,
# and a minimum number of speakers of French, Spanish and German.
# A crew member who works a flight has two flights off after it.
# Encoding: one Bool per (flight, person); all constraints are PB sums over them.
from paramita.modelling import Bool

def build(instance):
    attributes = instance["attributes"]  # per person: [steward, hostess, French, Spanish, German]
    required = instance["required_crew"]  # per flight: [crew size, stewards, hostesses, French, Spanish, German]
    n_people = len(attributes)
    n_flights = len(required)

    x = [[Bool(f"x_{f}_{p}") for p in range(n_people)] for f in range(n_flights)]
    cons = []

    # the crew of each flight has exactly the required number of people
    for f in range(n_flights):
        cons.append(sum(x[f]) == required[f][0])

    # each flight has at least the required number of stewards
    for f in range(n_flights):
        cons.append(sum(x[f][p] for p in range(n_people) if attributes[p][0] == 1) >= required[f][1])

    # each flight has at least the required number of hostesses
    for f in range(n_flights):
        cons.append(sum(x[f][p] for p in range(n_people) if attributes[p][1] == 1) >= required[f][2])

    # each flight has at least the required number of speakers of each language
    for f in range(n_flights):
        for k, lang in enumerate(["French", "Spanish", "German"]):
            cons.append(
                sum(x[f][p] for p in range(n_people) if attributes[p][2 + k] == 1) >= required[f][3 + k]
            )

    # after an attended flight, a crew member has two flights off:
    # at most one flight in any window of three consecutive flights
    for p in range(n_people):
        for f in range(n_flights - 2):
            cons.append(x[f][p] + x[f + 1][p] + x[f + 2][p] <= 1)

    return cons, {"crew": x}

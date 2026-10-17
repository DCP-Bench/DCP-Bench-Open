# Crew assignment: assign flight attendants to flights. Each flight needs a certain
# number of cabin crew, and they have to speak certain languages. Every cabin crew
# member has two flights off after an attended flight.
# Output crew[f][p] is 1 if person p is assigned to flight f, 0 otherwise.
import mip


def build(instance):
    attributes = instance["attributes"]   # attributes[p] = [steward, hostess, French, Spanish, German]
    required = instance["required_crew"]  # required[f] = [size, stewards, hostesses, French, Spanish, German]
    n_people = len(attributes)
    n_flights = len(required)

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    crew = [[m.add_var(f"crew_{f}_{p}", var_type=mip.BINARY) for p in range(n_people)]
            for f in range(n_flights)]

    # Each flight needs a certain number of cabin crew
    for f in range(n_flights):
        m += mip.xsum(crew[f][p] for p in range(n_people)) == required[f][0]

    # they have to speak certain languages (and the stewards and hostesses it needs)
    for f in range(n_flights):
        for k in range(1, 6):
            members = [p for p in range(n_people) if attributes[p][k - 1] == 1]
            m += mip.xsum(crew[f][p] for p in members) >= required[f][k]

    # Every cabin crew member has two flights off after an attended flight
    for p in range(n_people):
        for f in range(n_flights):
            for g in (f + 1, f + 2):
                if g < n_flights:
                    m += crew[f][p] + crew[g][p] <= 1

    outputs = {"crew": [[crew[f][p] for p in range(n_people)] for f in range(n_flights)]}
    return m, outputs

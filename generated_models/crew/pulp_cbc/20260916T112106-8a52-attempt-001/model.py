import pulp


def build(instance):
    """Airline crew rostering: staff every flight with the right size and skill
    mix, and give anyone who flies a break of two flights afterwards.
    """
    attributes = instance["attributes"]
    required = instance["required_crew"]
    persons = len(attributes)
    flights = len(required)
    skills = len(attributes[0]) if persons else 0

    problem = pulp.LpProblem("crew", pulp.LpMinimize)
    crew = pulp.LpVariable.dicts("crew", (range(flights), range(persons)),
                                 cat="Binary")

    for f in range(flights):
        problem += pulp.lpSum(crew[f][p] for p in range(persons)) == required[f][0]
        for j in range(skills):
            problem += pulp.lpSum(attributes[p][j] * crew[f][p]
                                  for p in range(persons)) >= required[f][j + 1]

    # After a flight, two flights off.
    for f in range(flights - 2):
        for p in range(persons):
            problem += crew[f][p] + crew[f + 1][p] + crew[f + 2][p] <= 1

    # The reference pins the count of people who fly at least once to a
    # variable whose domain starts at one, so at least one person flies.
    works = [pulp.LpVariable(f"works{p}", cat="Binary") for p in range(persons)]
    for p in range(persons):
        for f in range(flights):
            problem += crew[f][p] <= works[p]
    problem += pulp.lpSum(works) >= 1

    rows = [[crew[f][p] for p in range(persons)] for f in range(flights)]
    return problem, {"crew": rows}

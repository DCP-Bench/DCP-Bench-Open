"""Crew scheduling: staff every flight with enough cabin crew of each kind, with two flights off after each one worked."""
from docplex.mp.model import Model


def build(instance):
    attributes = instance["attributes"]        # per person: steward, hostess, French, Spanish, German
    required_crew = instance["required_crew"]  # per flight: crew size, then the minimum of each attribute
    persons = range(len(attributes))
    flights = range(len(required_crew))
    kinds = range(5)  # the five attribute columns the problem defines

    model = Model("crew")

    # crew[f, p] is 1 when person p works flight f.
    crew = model.binary_var_matrix(flights, persons, name="crew")

    for f in flights:
        # The flight has exactly the crew size it needs.
        model.add_constraint(model.sum(crew[f, p] for p in persons) == required_crew[f][0], ctname=f"size_{f}")
        # It has at least the required number of stewards, hostesses and speakers of each language.
        for k in kinds:
            model.add_constraint(model.sum(attributes[p][k] * crew[f, p] for p in persons)
                                 >= required_crew[f][k + 1], ctname=f"attribute_{f}_{k}")

    # After a flight, a person has at least the next two flights off.
    for f in range(len(required_crew) - 2):
        for p in persons:
            model.add_constraint(crew[f, p] + crew[f + 1, p] + crew[f + 2, p] <= 1, ctname=f"rest_{f}_{p}")

    # The reference counts the persons who work at least one flight in a variable
    # with domain 1..persons, so at least one person works somewhere.
    model.add_constraint(model.sum(crew.values()) >= 1, ctname="someone_works")

    return model, {"crew": [[crew[f, p] for p in persons] for f in flights]}

"""Crew scheduling: staff every flight with enough cabin crew of each kind, with two flights off after each one worked."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    attributes = instance["attributes"]        # per person: steward, hostess, French, Spanish, German
    required_crew = instance["required_crew"]  # per flight: crew size, then the minimum of each attribute
    persons = range(len(attributes))
    flights = range(len(required_crew))
    kinds = range(5)  # the five attribute columns the problem defines

    model = gp.Model("crew")

    # crew[f, p] is 1 when person p works flight f.
    crew = model.addVars(flights, persons, vtype=GRB.BINARY, name="crew")

    for f in flights:
        # The flight has exactly the crew size it needs.
        model.addConstr(crew.sum(f, "*") == required_crew[f][0], name=f"size[{f}]")
        # It has at least the required number of stewards, hostesses and speakers of each language.
        for k in kinds:
            model.addConstr(gp.quicksum(attributes[p][k] * crew[f, p] for p in persons)
                            >= required_crew[f][k + 1], name=f"attribute[{f},{k}]")

    # After a flight, a person has at least the next two flights off.
    for f in range(len(required_crew) - 2):
        for p in persons:
            model.addConstr(crew[f, p] + crew[f + 1, p] + crew[f + 2, p] <= 1, name=f"rest[{f},{p}]")

    # The reference counts the persons who work at least one flight in a variable
    # with domain 1..persons, so at least one person works somewhere.
    model.addConstr(crew.sum() >= 1, name="someone_works")

    return model, {"crew": [[crew[f, p] for p in persons] for f in flights]}

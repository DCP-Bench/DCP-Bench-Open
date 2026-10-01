# Car sequencing: order a production line of cars so that no option station is overloaded.
from ortools.sat.python import cp_model


def build(instance):
    at_most = instance["at_most"]    # at_most[o] cars out of any per_slots[o] consecutive ones may need option o
    per_slots = instance["per_slots"]
    demand = instance["demand"]      # demand[t] = number of cars of type t to produce
    requires = instance["requires"]  # requires[t][o] = 1 if a car of type t needs option o

    n_types = len(demand)
    n_options = len(at_most)
    n_cars = sum(demand)             # one slot on the line per car

    model = cp_model.CpModel()

    # is_type[s][t] is true when slot s holds a car of type t.
    is_type = [[model.new_bool_var(f"is_type_{s}_{t}") for t in range(n_types)]
               for s in range(n_cars)]

    # Every slot holds exactly one car.
    for s in range(n_cars):
        model.add_exactly_one(is_type[s])

    # The number of cars of each type in the sequence equals the demand for that type.
    for t in range(n_types):
        model.add(sum(is_type[s][t] for s in range(n_cars)) == demand[t])

    # needs[s][o] = 1 if the car in slot s requires option o. It is a sum of the type
    # literals, so it follows the car type without extra variables or element constraints.
    needs = [[sum(is_type[s][t] for t in range(n_types) if requires[t][o])
              for o in range(n_options)]
             for s in range(n_cars)]

    # Station capacity: in any window of per_slots[o] consecutive slots, at most
    # at_most[o] cars may require option o.
    for o in range(n_options):
        for start in range(n_cars - per_slots[o] + 1):
            model.add(sum(needs[s][o] for s in range(start, start + per_slots[o])) <= at_most[o])

    # sequence[s] is the car type in slot s (types are numbered from 0).
    sequence = [sum(t * is_type[s][t] for t in range(n_types)) for s in range(n_cars)]
    return model, {"sequence": sequence}

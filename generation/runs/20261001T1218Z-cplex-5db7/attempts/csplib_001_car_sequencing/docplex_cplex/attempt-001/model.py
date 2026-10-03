"""Car sequencing: put the ordered cars in a line so that no option station is overloaded.

Each car type needs some of the options (air-conditioning, sunroof, ...). Station o can
handle at most at_most[o] cars needing its option in any run of per_slots[o] consecutive
positions. The model finds the sequence of car types that meets the whole demand.
"""
from docplex.mp.model import Model


def build(instance):
    at_most = instance["at_most"]      # most cars needing option o in one window
    per_slots = instance["per_slots"]  # length of that window, in positions
    demand = instance["demand"]        # how many cars of each type are ordered
    requires = instance["requires"]    # requires[t][o] = 1 if type t needs option o

    n_types = len(demand)
    n_options = len(at_most)
    n_cars = sum(demand)               # one position per ordered car

    model = Model("car_sequencing")

    # on_line[s, t] is 1 when the car at position s is of type t.
    on_line = model.binary_var_matrix(range(n_cars), range(n_types), name="on_line")

    # Every position holds exactly one car.
    for s in range(n_cars):
        model.add_constraint(model.sum(on_line[s, t] for t in range(n_types)) == 1)

    # The number of cars of each type in the sequence equals the demand for that type.
    for t in range(n_types):
        model.add_constraint(model.sum(on_line[s, t] for s in range(n_cars)) == demand[t])

    # needs[s][o] is the number (0 or 1) of cars at position s that need option o. It is
    # an expression over on_line, not a variable, to keep the model small.
    needs = [[model.sum(requires[t][o] * on_line[s, t] for t in range(n_types))
              for o in range(n_options)] for s in range(n_cars)]

    # Capacity of each station: in every run of per_slots[o] consecutive positions,
    # at most at_most[o] cars need option o.
    for o in range(n_options):
        for s in range(n_cars - per_slots[o] + 1):
            model.add_constraint(
                model.sum(needs[k][o] for k in range(s, s + per_slots[o])) <= at_most[o])

    # The declared output: the car type at each position, read back from the assignment.
    sequence = [model.sum(t * on_line[s, t] for t in range(n_types)) for s in range(n_cars)]

    return model, {"sequence": sequence}

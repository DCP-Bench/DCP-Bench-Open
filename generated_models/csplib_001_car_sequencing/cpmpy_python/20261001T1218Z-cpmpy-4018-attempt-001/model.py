# Car sequencing: order a production line of cars so that no option station is overloaded.
import cpmpy as cp


def build(instance):
    at_most = instance["at_most"]    # at_most[o] cars out of any per_slots[o] consecutive ones may need option o
    per_slots = instance["per_slots"]
    demand = instance["demand"]      # demand[t] = number of cars of type t to produce
    requires = instance["requires"]  # requires[t][o] = 1 if a car of type t needs option o

    n_types = len(demand)
    n_options = len(at_most)
    n_cars = sum(demand)             # one slot on the line per car, so the line length comes from the demand

    # sequence[s] is the car type in slot s (types are numbered from 0).
    sequence = cp.intvar(0, n_types - 1, shape=n_cars, name="sequence")

    # is_type[s, t] is true exactly when slot s holds a car of type t. Window sums over
    # these Booleans stay linear, which is cheaper than an element constraint per slot.
    is_type = cp.boolvar(shape=(n_cars, n_types), name="is_type")

    model = cp.Model()

    # Link the type variable of each slot to its Boolean indicators.
    for s in range(n_cars):
        for t in range(n_types):
            model += is_type[s, t] == (sequence[s] == t)

    # The number of cars of each type on the line equals the demand for that type.
    for t in range(n_types):
        model += cp.sum(is_type[:, t]) == demand[t]

    # needs[s][o] is the number (0 or 1) of options o required by the car in slot s: the sum of the
    # indicators of the car types that require option o.
    needs = [[cp.sum([is_type[s, t] for t in range(n_types) if requires[t][o]])
              for o in range(n_options)]
             for s in range(n_cars)]

    # Station capacity: in any window of per_slots[o] consecutive slots, at most at_most[o] cars
    # may require option o. A line shorter than the window has no window to check.
    for o in range(n_options):
        for start in range(n_cars - per_slots[o] + 1):
            model += cp.sum([needs[s][o] for s in range(start, start + per_slots[o])]) <= at_most[o]

    return model, {"sequence": sequence}

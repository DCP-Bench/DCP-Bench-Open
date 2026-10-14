"""Car sequencing: arrange the cars of an order on an assembly line so that no
option station is overloaded.

Each car has a type, and each type needs some of the options (air-conditioning,
sunroof, ...). Station o can cope with at most at_most[o] cars needing its option
in any run of per_slots[o] consecutive positions. The model finds the sequence
of car types that serves the whole demand within these capacities.
"""
import pulp


def build(instance):
    at_most = instance["at_most"]      # most cars needing option o in one window
    per_slots = instance["per_slots"]  # length of that window, in positions
    demand = instance["demand"]        # how many cars of each type are ordered
    requires = instance["requires"]    # requires[t][o] = 1 if type t needs option o

    n_types = len(demand)
    n_options = len(at_most)
    n_cars = sum(demand)               # one position per ordered car

    problem = pulp.LpProblem("car_sequencing", pulp.LpMinimize)

    # on_line[s][t] = 1 if the car at position s is of type t.
    on_line = [[pulp.LpVariable(f"on_line_{s}_{t}", cat="Binary") for t in range(n_types)]
               for s in range(n_cars)]

    # sequence[s] = the type of the car at position s (the declared output).
    # It is a bounded integer tied to the assignment matrix, so enumeration of a
    # second solution only has to cut over these n_cars variables.
    sequence = [pulp.LpVariable(f"sequence_{s}", 0, n_types - 1, cat="Integer")
                for s in range(n_cars)]

    # every position holds exactly one car, and sequence reads its type back
    for s in range(n_cars):
        problem += pulp.lpSum(on_line[s]) == 1
        problem += sequence[s] == pulp.lpSum(t * on_line[s][t] for t in range(n_types))

    # the number of cars of each type in the sequence equals the demand for that type
    for t in range(n_types):
        problem += pulp.lpSum(on_line[s][t] for s in range(n_cars)) == demand[t]

    # needs[s][o] = 1 if the car at position s needs option o, i.e. the option
    # flags of its type. A separate 0/1 variable keeps the window rows short.
    needs = [[pulp.LpVariable(f"needs_{s}_{o}", cat="Binary") for o in range(n_options)]
             for s in range(n_cars)]
    for s in range(n_cars):
        for o in range(n_options):
            problem += needs[s][o] == pulp.lpSum(requires[t][o] * on_line[s][t]
                                                 for t in range(n_types))

    # capacity of each station: in every run of per_slots[o] consecutive positions,
    # at most at_most[o] cars need option o
    for o in range(n_options):
        for s in range(n_cars - per_slots[o] + 1):
            problem += pulp.lpSum(needs[k][o] for k in range(s, s + per_slots[o])) <= at_most[o]

    return problem, {"sequence": sequence}

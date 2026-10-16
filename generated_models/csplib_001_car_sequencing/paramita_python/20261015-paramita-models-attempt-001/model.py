# Car sequencing (CSPLib prob001): cars of several types are arranged on an
# assembly line so that each option station never has to handle more cars
# than its capacity allows in any window of consecutive cars.
# The instance gives, per car type, the demand and which options it requires;
# per option, the capacity at_most and the window length per_slots:
# in any per_slots[o] consecutive cars, at most at_most[o] cars require option o.
# Output: the car type (numbered from 0) at each position of the line.

from paramita.modelling import Bool


def build(instance):
    demand = instance["demand"]          # number of cars of each type
    requires = instance["requires"]      # requires[t][o]: cars of type t need option o
    at_most = instance["at_most"]        # capacity of each option station
    per_slots = instance["per_slots"]    # window length of each option station

    n_types = len(demand)
    n_opts = len(at_most)
    n_cars = sum(demand)                 # one position per car

    # car type t at position p: one-hot Bools
    x = [[Bool(f"car_{p}_{t}") for t in range(n_types)] for p in range(n_cars)]
    cons = []

    # every position of the line holds exactly one car
    cons += [sum(x[p]) == 1 for p in range(n_cars)]

    # each car type is built as many times as its demand
    cons += [sum(x[p][t] for p in range(n_cars)) == demand[t] for t in range(n_types)]

    # needs[p][o]: the car at position p requires option o (1) or not (0)
    needs = [
        [sum(x[p][t] for t in range(n_types) if requires[t][o]) for o in range(n_opts)]
        for p in range(n_cars)
    ]

    # the cars requiring an option must not be bunched together:
    # in every window of per_slots[o] consecutive positions, at most at_most[o] of them require option o
    for o in range(n_opts):
        if not any(requires[t][o] for t in range(n_types)):
            continue
        w = per_slots[o]
        for start in range(n_cars - w + 1):
            cons.append(sum(needs[p][o] for p in range(start, start + w)) <= at_most[o])

    # the car type at each position of the line
    sequence = [sum(t * x[p][t] for t in range(1, n_types)) for p in range(n_cars)]
    return cons, {"sequence": sequence}

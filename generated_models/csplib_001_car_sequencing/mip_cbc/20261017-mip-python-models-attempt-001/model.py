# CSPLib 001 car sequencing: cars of several types (demand per type) are put in one
# assembly-line sequence so that no option station is over capacity.
# Output: sequence, the car type at each position, types numbered from 0.
import mip


def build(instance):
    demand = instance["demand"]
    requires = instance["requires"]
    at_most = instance["at_most"]
    per_slots = instance["per_slots"]
    n_types = len(demand)
    n_cars = sum(demand)
    n_opts = len(at_most)

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[p][c] = 1 when position p carries a car of type c.
    x = [[m.add_var(f"x_{p}_{c}", var_type=mip.BINARY) for c in range(n_types)]
         for p in range(n_cars)]
    seq = [m.add_var(f"seq_{p}", lb=0, ub=n_types - 1, var_type=mip.INTEGER)
           for p in range(n_cars)]

    # Each position is filled by exactly one car, and the sequence reads its type.
    for p in range(n_cars):
        # Each position holds exactly one car type.
        m += mip.xsum(x[p]) == 1
        # The sequence value is the type of the car at that position.
        m += seq[p] == mip.xsum(c * x[p][c] for c in range(n_types))

    # Each car type is produced as many times as its demand.
    for c in range(n_types):
        # The demand for each car type is met exactly.
        m += mip.xsum(x[p][c] for p in range(n_cars)) == demand[c]

    # Cars requiring an option must not be bunched together: in every window of
    # per_slots consecutive positions, at most at_most cars need that option.
    for o in range(n_opts):
        k = per_slots[o]
        needing = [c for c in range(n_types) if requires[c][o]]
        for start in range(n_cars - k + 1):
            # Each station handles at most a certain number of cars in its window.
            m += mip.xsum(x[p][c] for p in range(start, start + k) for c in needing) <= at_most[o]

    # Satisfaction problem: no objective.
    return m, {"sequence": seq}

# Template design: decide how many sheets to print from each template, and how many copies
# of each variation to put on each template, so that every variation's demand is met, every
# slot of a template is used, and as few sheets as possible are printed.
import z3


def build(instance):
    n_slots = instance["n_slots"]          # slots on a template
    n_templates = instance["n_templates"]  # number of templates
    n_var = instance["n_var"]              # number of variations
    demand = instance["demand"]            # demand of each variation
    ub = max(demand)                       # upper bound on the sheets printed per template

    # The unknowns are bit-vectors, because Z3's optimiser handles the product of two
    # integer variables badly but bit-blasts the product of two bit-vectors. The width holds
    # the largest value that appears: the copies of one variation over all templates, at
    # most n_templates * ub * n_var, the slots times the total production in the implied
    # constraint below, and the sum of the demands.
    largest = max(n_templates * ub * n_var, n_slots * n_templates * ub, n_slots, sum(demand))
    width = largest.bit_length() + 1

    def const(value):
        return z3.BitVecVal(value, width)

    # production[t] is the number of sheets printed from template t, between 1 and ub.
    production = [z3.BitVec(f"production_{t}", width) for t in range(n_templates)]
    # layout[t][v] is the number of copies of variation v on template t, between 0 and
    # n_var (the reference's domain).
    layout = [[z3.BitVec(f"layout_{t}_{v}", width) for v in range(n_var)]
              for t in range(n_templates)]

    solver = z3.Solver()

    for t in range(n_templates):
        solver.add(z3.UGE(production[t], const(1)), z3.ULE(production[t], const(ub)))
        for v in range(n_var):
            solver.add(z3.ULE(layout[t][v], const(n_var)))

    # All the slots of every template are populated.
    for t in range(n_templates):
        solver.add(sum(layout[t]) == const(n_slots))

    # Meet the demand: the copies of variation v printed over all templates (sheets of
    # template t times the copies of v on it) are at least its demand.
    for v in range(n_var):
        printed = sum(production[t] * layout[t][v] for t in range(n_templates))
        solver.add(z3.UGE(printed, const(demand[v])))

    # Implied: every template fills all its slots, so the sheets cover the total demand.
    total_sheets = sum(production)
    solver.add(z3.UGE(const(n_slots) * total_sheets, const(sum(demand))))

    # The declared outputs are integers: read the bit-vectors as unsigned numbers.
    outputs = {
        "production": [z3.BV2Int(p) for p in production],
        "layout": [[z3.BV2Int(l) for l in row] for row in layout],
    }

    # Minimize the number of printed sheets.
    return solver, outputs, ("minimize", z3.BV2Int(total_sheets))

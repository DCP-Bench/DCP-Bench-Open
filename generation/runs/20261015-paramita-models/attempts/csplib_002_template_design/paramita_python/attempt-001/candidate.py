"""csplib_002 template design: print each variation from templates of n_slots items, minimising sheets.

Templates are printed from a mother sheet; each template carries n_slots item positions,
each holding one copy of one variation. Each variation's demand must be met by the
copies printed over all sheets. The number of sheets for each template is minimised.
"""
from paramita.modelling import Bool, And, Or, Iff, If


def build(instance):
    n_slots = instance["n_slots"]
    n_templates = instance["n_templates"]
    n_var = instance["n_var"]
    demand = instance["demand"]
    max_sheets = max(demand)

    # copies[t][i][v] = variation i occupies v slots of template t (one-hot over 0..n_slots)
    copies = [
        [{v: Bool(f"copies_{t}_{i}_{v}") for v in range(n_slots + 1)} for i in range(n_var)]
        for t in range(n_templates)
    ]
    # sheets[t][p-1] = template t is printed on at least p sheets (unary, p in 1..max_sheets)
    sheets = [[Bool(f"sheets_ge_{t}_{p}") for p in range(1, max_sheets + 1)] for t in range(n_templates)]

    def sheets_at_least(t, k):
        # literal for "sheets of template t >= k"; k must be in 1..max_sheets
        return sheets[t][k - 1]

    cons = []

    # each variation takes exactly one number of slots on each template
    for t in range(n_templates):
        for i in range(n_var):
            cons.append(sum(copies[t][i].values()) == 1)

    # each template has exactly n_slots items printed on it
    for t in range(n_templates):
        cons.append(sum(v * b for i in range(n_var) for v, b in copies[t][i].items() if v > 0) == n_slots)

    # unary order for the sheet counts: at least p sheets implies at least p-1 sheets
    for t in range(n_templates):
        for p in range(2, max_sheets + 1):
            cons.append(If(sheets[t][p - 1], sheets[t][p - 2]))

    # demand of each variation must be met over all templates:
    # sum_t copies(t,i) * sheets(t) >= demand[i], with each product written as capped unary bits
    # q_k(t,i) <=> copies(t,i) * sheets(t) >= k, for k = 1..demand[i]
    cover_bits = {}
    for i in range(n_var):
        d = demand[i]
        for t in range(n_templates):
            for k in range(1, d + 1):
                q = Bool(f"cover_{t}_{i}_{k}")
                cover_bits[(t, i, k)] = q
                options = []
                for v in range(1, n_slots + 1):
                    need = -(-k // v)  # ceil(k / v) sheets needed when v copies are on each sheet
                    if need <= max_sheets:
                        options.append(And(copies[t][i][v], sheets_at_least(t, need)))
                cons.append(Iff(q, Or(options)))

    for i in range(n_var):
        d = demand[i]
        # the copies of variation i printed in total must cover its demand
        cons.append(sum(cover_bits[(t, i, k)] for t in range(n_templates) for k in range(1, d + 1)) >= d)

    # symmetry: the templates are interchangeable, so sort them by sheet count
    for t in range(n_templates - 1):
        for p in range(1, max_sheets + 1):
            cons.append(If(sheets[t + 1][p - 1], sheets[t][p - 1]))

    # redundant: every template has n_slots items, so n_slots * total sheets covers the total demand
    cons.append(n_slots * sum(sum(sheets[t]) for t in range(n_templates)) >= sum(demand))

    layout = [[sum(v * b for v, b in copies[t][i].items()) for i in range(n_var)] for t in range(n_templates)]
    production = [sum(sheets[t]) for t in range(n_templates)]

    # minimise the total number of printed sheets
    total_sheets = sum(production)
    return cons, {"layout": layout, "production": production}, ("minimize", total_sheets)

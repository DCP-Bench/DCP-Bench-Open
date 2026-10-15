"""csplib_002 template design: print each variation from templates of n_slots items, minimising sheets.

Templates are printed from a mother sheet; each template carries n_slots item positions,
each holding one copy of one variation. Each variation's demand must be met by the
copies printed over all sheets. The number of sheets printed is minimised.
"""
from paramita.modelling import Bool, And, Iff


def build(instance):
    n_slots = instance["n_slots"]
    n_templates = instance["n_templates"]
    n_var = instance["n_var"]
    demand = instance["demand"]
    max_sheets = max(demand)
    n_bits = max_sheets.bit_length()

    # copies[t][i][v] = variation i occupies v item positions of template t (one-hot over 0..n_slots)
    copies = [
        [{v: Bool(f"copies_{t}_{i}_{v}") for v in range(n_slots + 1)} for i in range(n_var)]
        for t in range(n_templates)
    ]
    # sheets[t][b] = bit b of the number of sheets printed from template t (binary)
    sheets = [[Bool(f"sheets_{t}_bit_{b}") for b in range(n_bits)] for t in range(n_templates)]

    def sheet_count(t):
        return sum((2**b) * sheets[t][b] for b in range(n_bits))

    cons = []

    # each variation takes exactly one number of positions on each template
    for t in range(n_templates):
        for i in range(n_var):
            cons.append(sum(copies[t][i].values()) == 1)

    # each template has exactly n_slots items printed on it
    for t in range(n_templates):
        cons.append(sum(v * b for i in range(n_var) for v, b in copies[t][i].items() if v > 0) == n_slots)

    # the sheet count of each template is at most the largest demand
    for t in range(n_templates):
        cons.append(sheet_count(t) <= max_sheets)

    # demand of each variation must be met over all templates:
    # copies(t,i) * sheets(t) = sum_v sum_b v * 2^b * [copies(t,i) = v and bit b of sheets(t)]
    for i in range(n_var):
        d = demand[i]
        products = []
        for t in range(n_templates):
            for v in range(1, n_slots + 1):
                for b in range(n_bits):
                    both = Bool(f"both_{t}_{i}_{v}_{b}")
                    cons.append(Iff(both, And(copies[t][i][v], sheets[t][b])))
                    products.append(v * (2**b) * both)
        cons.append(sum(products) >= d)

    # symmetry: the templates are interchangeable, so sort them by sheet count
    for t in range(n_templates - 1):
        cons.append(sheet_count(t) >= sheet_count(t + 1))

    # redundant: every template has n_slots items, so n_slots * total sheets covers the total demand
    total_sheets = sum(sheet_count(t) for t in range(n_templates))
    cons.append(n_slots * total_sheets >= sum(demand))

    layout = [[sum(v * b for v, b in copies[t][i].items()) for i in range(n_var)] for t in range(n_templates)]
    production = [sheet_count(t) for t in range(n_templates)]

    return cons, {"layout": layout, "production": production}, ("minimize", total_sheets)

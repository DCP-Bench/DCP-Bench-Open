from paramita.modelling import Bool, If


# Template design: print mother sheets from several templates; each template
# has n_slots slots filled with copies of variations, and the printed copies of
# every variation must cover its demand. Minimise the total number of sheets.
#
# Encoding: the number of sheets of a template and the copies of a variation
# on a template are both binary. Their product is a sum of one auxiliary Bool
# per (copy bit, sheet bit), so every PB weight is a power of two and few
# auxiliaries are needed (unary or one-hot copies gave more auxiliaries and
# a slower optimum proof).
def build(instance):
    n_templates = instance["n_templates"]
    n_var = instance["n_var"]
    n_slots = instance["n_slots"]
    demand = instance["demand"]

    # a template printed more often than the largest demand is never needed, since
    # every variation on it is then covered (bound derived from the demand)
    max_sheets = max(demand)
    n_bits = max_sheets.bit_length()
    # copies of one variation on one template: at most n_var (and n_slots). The
    # n_var cap is a bound of the reference model, not of the description: a
    # solution with more copies of a variation on one template is rejected.
    cap = min(n_var, n_slots)
    k_bits = cap.bit_length()

    # bit[t][j]: bit j of the number of sheets printed from template t
    bit = [[Bool(f"sheets_{t}_bit_{j}") for j in range(n_bits)] for t in range(n_templates)]
    production = [sum((2 ** j) * bit[t][j] for j in range(n_bits)) for t in range(n_templates)]

    # kb[t][v][i]: bit i of the number of copies of variation v on template t
    kb = [[[Bool(f"copies_{t}_{v}_bit_{i}") for i in range(k_bits)]
           for v in range(n_var)] for t in range(n_templates)]
    layout = [[sum((2 ** i) * kb[t][v][i] for i in range(k_bits)) for v in range(n_var)]
              for t in range(n_templates)]

    cons = []

    # each template has n_slots slots, all filled with copies of variations
    # (an extra copy never hurts, so filling every slot keeps the optimum)
    for t in range(n_templates):
        cons.append(sum(layout[t]) == n_slots)

    # the number of copies of a variation on a template is at most the cap
    for t in range(n_templates):
        for v in range(n_var):
            cons.append(layout[t][v] <= cap)

    # the number of sheets of a template is at most the largest demand
    for t in range(n_templates):
        cons.append(production[t] <= max_sheets)

    # the demand of each variation is met: copies per sheet times sheets, summed over templates;
    # m[t][v][i][j] implies "bit i of the copies is set and bit j of the sheets is set"
    # (it only helps a >= constraint, so one direction is enough)
    for v in range(n_var):
        terms = []
        for t in range(n_templates):
            for i in range(k_bits):
                for j in range(n_bits):
                    m = Bool(f"printed_{t}_{v}_{i}_{j}")
                    cons.append(If(m, kb[t][v][i] & bit[t][j]))
                    terms.append((2 ** (i + j)) * m)
        cons.append(sum(terms) >= demand[v])

    # all templates carry n_slots copies per sheet, so the total number of sheets
    # times n_slots covers the total demand (redundant bound)
    cons.append(sum(production) * n_slots >= sum(demand))

    # the templates are interchangeable: order them by their number of sheets
    for t in range(n_templates - 1):
        cons.append(production[t] >= production[t + 1])

    # variations with equal demand are interchangeable: order their copy vectors
    # (one number per variation, template 0 most significant)
    base = cap + 1
    vec = [sum(base ** (n_templates - 1 - t) * layout[t][v] for t in range(n_templates))
           for v in range(n_var)]
    for v in range(n_var - 1):
        if demand[v] == demand[v + 1]:
            cons.append(vec[v] >= vec[v + 1])

    # minimise the total number of printed sheets
    total = sum(production)
    return cons, {"layout": layout, "production": production}, ("minimize", total)

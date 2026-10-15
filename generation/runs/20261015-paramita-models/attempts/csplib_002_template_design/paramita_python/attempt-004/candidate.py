from paramita.modelling import Bool, Iff


# Template design: print a number of mother sheets from each of several
# templates; each template carries several variations (in n_slots slots),
# and the printed copies of each variation must cover its demand.
# Minimise the total number of printed sheets.
#
# Encoding: the sheet count of each template is a binary number, the copies of
# each variation on a template are one-hot. Their product is linearised with one
# auxiliary Bool per (template, variation, copies value, bit).
def build(instance):
    n_templates = instance["n_templates"]
    n_var = instance["n_var"]
    n_slots = instance["n_slots"]
    demand = instance["demand"]

    # The largest demand bounds every sheet count: a template printed more often
    # than the largest demand is never needed, since each of its variations is
    # then already covered.
    max_sheets = max(demand)
    n_bits = max_sheets.bit_length()

    # production[t] = number of printed sheets of template t, in binary
    bits = [[Bool(f"sheets_{t}_bit_{j}") for j in range(n_bits)] for t in range(n_templates)]
    production = [sum((2 ** j) * bits[t][j] for j in range(n_bits)) for t in range(n_templates)]

    # copies[t][v][k] = 1 if template t carries exactly k copies of variation v
    copies = [[[Bool(f"copies_{t}_{v}_{k}") for k in range(n_slots + 1)]
               for v in range(n_var)] for t in range(n_templates)]

    cons = []

    # the sheet count of a template is at most the largest demand
    cons += [sum((2 ** j) * bits[t][j] for j in range(n_bits)) <= max_sheets
             for t in range(n_templates)]

    # each variation count on a template is exactly one of 0..n_slots
    for t in range(n_templates):
        for v in range(n_var):
            cons.append(sum(copies[t][v]) == 1)

    # a template holds at most n_slots variations (mother sheet slots)
    for t in range(n_templates):
        cons.append(sum(k * copies[t][v][k] for v in range(n_var) for k in range(n_slots + 1))
                    <= n_slots)

    # the printed copies of each variation (copies per sheet times sheets) meet its demand;
    # aux[t][v][k][j] <-> the template carries k copies of v and bit j of its sheet count is set
    aux = {}
    for t in range(n_templates):
        for v in range(n_var):
            for k in range(1, n_slots + 1):
                for j in range(n_bits):
                    m = Bool(f"printed_{t}_{v}_{k}_{j}")
                    aux[t, v, k, j] = m
                    cons.append(Iff(m, copies[t][v][k] & bits[t][j]))
    for v in range(n_var):
        cons.append(sum(k * (2 ** j) * aux[t, v, k, j]
                        for t in range(n_templates) for k in range(1, n_slots + 1)
                        for j in range(n_bits)) >= demand[v])

    # the templates are interchangeable: order them by their sheet count
    for t in range(n_templates - 1):
        cons.append(production[t] >= production[t + 1])

    layout = [[sum(k * copies[t][v][k] for k in range(n_slots + 1)) for v in range(n_var)]
              for t in range(n_templates)]

    # total number of printed sheets
    total = sum(production)
    return cons, {"layout": layout, "production": production}, ("minimize", total)

# Media selection: choose advertising media so that every target audience is
# reached by at least one chosen medium, at minimum total campaign cost.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    incidence_matrix = instance["incidence_matrix"]  # [t][m] = 1 if medium m reaches audience t
    media_costs = instance["media_costs"]
    num_audiences = len(instance["target_audiences"])
    num_media = len(instance["advertising_media"])

    pool = IDPool()
    # is_selected[m] is true when medium m is part of the campaign.
    is_selected = [pool.id(("is_selected", m)) for m in range(num_media)]

    formula = WCNF()

    # Each target audience must be covered by at least one selected medium.
    for t in range(num_audiences):
        lits = [is_selected[m] for m in range(num_media) if incidence_matrix[t][m] != 0]
        weights = [incidence_matrix[t][m] for m in range(num_media) if incidence_matrix[t][m] != 0]
        if all(w == 1 for w in weights):
            formula.append(lits)   # an empty clause here means the audience cannot be reached
        else:
            formula.extend(PBEnc.geq(lits=lits, weights=weights, bound=1, vpool=pool).clauses)

    # min_total_cost is the cost of the selected media. Its domain runs from
    # the sum of the negative costs to the sum of the positive ones.
    low = sum(c for c in media_costs if c < 0)
    high = sum(c for c in media_costs if c > 0)
    min_total_cost = Integer("min_total_cost", low, max(high, low + 1), vpool=pool)
    formula.extend(IntegerEngine(vars=[min_total_cost], vpool=pool).clausify().clauses)

    # The cost is tied to the selection by a running sum over the media, one
    # literal per partial sum that can occur; unit propagation then fixes the
    # cost once the selection is fixed.
    # partial[v] is true when the media considered so far cost v.
    start = pool.id(("partial", 0, 0))
    formula.append([start])
    partial = {0: start}
    for m in range(num_media):
        nxt = {}
        for v in partial:
            for w in (v, v + media_costs[m]):
                if w not in nxt:
                    nxt[w] = pool.id(("partial", m + 1, w))
        for v, lit in partial.items():
            # medium m not selected: the sum stays; selected: it grows by its cost
            formula.append([-lit, is_selected[m], nxt[v]])
            formula.append([-lit, -is_selected[m], nxt[v + media_costs[m]]])
        partial = nxt
    for v, lit in partial.items():
        formula.append([-lit, min_total_cost.equals(v)])
    for v in range(low, max(high, low + 1) + 1):
        if v not in partial:
            formula.append([-min_total_cost.equals(v)])

    # Minimise the campaign cost: selecting medium m pays its cost (a
    # negative cost is paid by leaving it out, a constant shift).
    for m in range(num_media):
        if media_costs[m] > 0:
            formula.append([-is_selected[m]], weight=media_costs[m])
        elif media_costs[m] < 0:
            formula.append([is_selected[m]], weight=-media_costs[m])

    return formula, {"is_selected": is_selected, "min_total_cost": min_total_cost}

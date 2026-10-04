# Football squad: buy goalkeepers, defenders, midfielders and strikers within
# the required numbers of each and at least eleven players in total, spending
# as close to the GBP 30 million limit as possible without going over.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc
from pysat.pb import EncType as PBType


def build(instance):
    # The problem has no instance data: the prices, group sizes and limits are
    # fixed by the problem statement and mirrored from the reference, prices
    # in GBP thousands.
    budget = 30000
    costs = [[730, 1280, 3880],                                          # goalkeepers
             [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],            # defenders
             [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],  # midfielders
             [4460, 6470, 7780, 8390, 9500]]                             # strikers
    min_max = [[1, 1], [2, 8], [3, 10], [2, 5]]   # how many of each group to buy
    min_players = 11

    players = [(g, k) for g in range(len(costs)) for k in range(len(costs[g]))]
    price = {p: costs[p[0]][p[1]] for p in players}

    # A feasible squad, built greedily, gives a lower bound on the best spend:
    # the cheapest players each group requires, then the cheapest others up to
    # eleven, then any further player that still fits, dearest first. Every
    # optimal squad spends at least this much, so z need not go lower.
    squad = []
    for g in range(len(costs)):
        squad += sorted((p for p in players if p[0] == g), key=price.get)[:min_max[g][0]]
    def room(p):
        return sum(1 for q in squad if q[0] == p[0]) < min_max[p[0]][1]
    for p in sorted(players, key=price.get):
        if len(squad) >= min_players:
            break
        if p not in squad and room(p):
            squad.append(p)
    spend = sum(price[p] for p in squad)
    if spend <= budget and len(squad) >= min_players:
        for p in sorted(players, key=price.get, reverse=True):
            if p not in squad and room(p) and spend + price[p] <= budget:
                squad.append(p)
                spend += price[p]
        lower = spend
    else:
        lower = 0

    pool = IDPool()
    # x[p] is true when player p is bought.
    x = {p: pool.id(("x", p)) for p in players}
    # z is the total price of the players bought, at most the budget.
    z = Integer("z", lower, max(budget, lower + 1), vpool=pool)
    engine = IntegerEngine(vars=[z], vpool=pool)
    if budget < lower + 1:
        engine.add_linear(z <= budget)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Each group is bought within its minimum and maximum number of players.
    for g in range(len(costs)):
        group = [x[p] for p in players if p[0] == g]
        formula.extend(CardEnc.atleast(lits=group, bound=min_max[g][0], vpool=pool,
                                       encoding=EncType.seqcounter).clauses)
        if min_max[g][1] < len(group):
            formula.extend(CardEnc.atmost(lits=group, bound=min_max[g][1], vpool=pool,
                                          encoding=EncType.seqcounter).clauses)

    # At least eleven players are bought in total.
    formula.extend(CardEnc.atleast(lits=list(x.values()), bound=min_players, vpool=pool,
                                   encoding=EncType.seqcounter).clauses)

    # z is the total price of the players bought. z's value is spelled out
    # in binary digits, offset from its lower bound, value by value; the sum
    # is then a pseudo-Boolean equation over those few digits and the
    # players. A sum over z's own value literals would carry thousands of
    # distinct weights.
    n_bits = max(budget - lower, 1).bit_length()
    bits = [pool.id(("z bit", k)) for k in range(n_bits)]
    for v in range(lower, max(budget, lower + 1) + 1):
        for k in range(n_bits):
            formula.append([-z.equals(v), bits[k] if ((v - lower) >> k) & 1 else -bits[k]])
    formula.extend(PBEnc.equals(lits=bits + [x[p] for p in players],
                                weights=[1 << k for k in range(n_bits)]
                                + [-price[p] for p in players],
                                bound=-lower, vpool=pool, encoding=PBType.adder).clauses)

    # Maximise the spend: every player not bought pays his price, so RC2
    # minimises the shortfall from the price of all players.
    for p in players:
        formula.append([x[p]], weight=price[p])

    return formula, {"z": z}

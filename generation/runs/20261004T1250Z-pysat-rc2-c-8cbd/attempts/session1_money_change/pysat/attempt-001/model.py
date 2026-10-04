# Money change: pay an exact amount with the coins available (a limited
# number of each value), using as few coins as possible.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer
from pysat.pb import PBEnc


def build(instance):
    amount = instance["amount"]
    types_of_coins = instance["types_of_coins"]  # value of each coin type
    available_coins = instance["available_coins"]
    n = len(types_of_coins)

    pool = IDPool()
    formula = WCNF()

    # coin_counts[i] is the number of coins of type i given, in the
    # reference's domain 0..max(available_coins). Coupled encoding: the value
    # literals are the output, the order literals ("at least v coins of type
    # i") state the sum and the objective.
    top = max(max(available_coins), 1)
    coin_counts = [Integer(f"coin_counts_{i}", 0, top, encoding="coupled", vpool=pool)
                   for i in range(n)]
    for x in coin_counts:
        formula.extend(x.domain_clauses())

    # No more coins of a type are given than are available.
    for i in range(n):
        if available_coins[i] < top:
            formula.append([-coin_counts[i].ge(max(available_coins[i], 0) + 1)])

    # The coins given add up to exactly the amount: each order literal
    # coin_counts[i] >= v stands for one more coin of value types_of_coins[i].
    lits = [coin_counts[i].ge(v) for i in range(n) for v in range(1, top + 1)]
    weights = [types_of_coins[i] for i in range(n) for v in range(1, top + 1)]
    formula.extend(PBEnc.equals(lits=lits, weights=weights, bound=amount,
                                vpool=pool).clauses)

    # Minimise the number of coins: every coin given pays 1.
    for lit in lits:
        formula.append([-lit], weight=1)

    return formula, {"coin_counts": coin_counts}

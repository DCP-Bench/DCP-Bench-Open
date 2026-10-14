# Chess sets: a joinery decides how many small and large boxwood chess sets to
# make per week, within its lathe hours and boxwood supply, to maximise profit.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # The problem has no instance data: every number below is fixed by the
    # problem statement and mirrored from the reference.
    max_sets = 100                         # domain of each set count in the reference
    boxwood_kg = {"small": 1, "large": 3}  # boxwood per set
    boxwood_supply = 200                   # kg per week
    lathe_hours = {"small": 3, "large": 2}
    lathe_supply = 160                     # 4 lathes x 40 hours
    profit = {"small": 5, "large": 20}     # dollars per set
    max_total = 10000                      # domain of max_profit in the reference

    pool = IDPool()
    # small_set and large_set are the numbers of sets made. Coupled encoding:
    # the order half serves the resource sums and the profit thresholds, the
    # direct half the "== v" literals used below and by the runner.
    small_set = Integer("small_set", 0, max_sets, encoding="coupled", vpool=pool)
    large_set = Integer("large_set", 0, max_sets, encoding="coupled", vpool=pool)
    # max_profit is the week's profit.
    max_profit = Integer("max_profit", 0, max_total, vpool=pool)
    engine = IntegerEngine(vars=[small_set, large_set, max_profit], vpool=pool)

    # Boxwood: the sets made use at most the boxwood obtainable.
    engine.add_linear(boxwood_kg["small"] * small_set + boxwood_kg["large"] * large_set
                      <= boxwood_supply)
    # Lathes: the sets made need at most the lathe-hours available.
    engine.add_linear(lathe_hours["small"] * small_set + lathe_hours["large"] * large_set
                      <= lathe_supply)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # max_profit is 5 per small set plus 20 per large set. Stated pair by
    # pair over the two counts' values: max_profit's domain has ten thousand
    # values, and a linear constraint over it would hand the encoder ten
    # thousand weighted literals, while these are 101 x 101 short clauses.
    for a in range(max_sets + 1):
        for b in range(max_sets + 1):
            value = profit["small"] * a + profit["large"] * b
            if value <= max_total:
                formula.append([-small_set.equals(a), -large_set.equals(b),
                                max_profit.equals(value)])
            else:
                formula.append([-small_set.equals(a), -large_set.equals(b)])

    # Maximise the profit: every small set not made, up to the 100 the
    # domain allows, pays 5 and every large set not made pays 20, so RC2
    # minimises the shortfall from the profit of 100 of each.
    for v in range(1, max_sets + 1):
        formula.append([small_set.ge(v)], weight=profit["small"])
        formula.append([large_set.ge(v)], weight=profit["large"])

    return formula, {"small_set": small_set, "large_set": large_set,
                     "max_profit": max_profit}

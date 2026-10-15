# Chess set production: how many small and large boxwood chess sets to make per week
# to maximise profit, subject to lathe hours and boxwood supply.

from pyscipopt import Model


def build(instance):
    # Problem constants from the description (the instance carries no fields)
    lathe_hours = 4 * 40      # four lathes, each with a 40 hour week
    boxwood_kg = 200          # boxwood available per week

    m = Model("chess_set")

    small_set = m.addVar(name="small_set", vtype="I", lb=0)  # small sets made per week
    large_set = m.addVar(name="large_set", vtype="I", lb=0)  # large sets made per week

    # a small set needs 3 lathe hours and a large set needs 2 lathe hours
    m.addCons(3 * small_set + 2 * large_set <= lathe_hours)

    # a small set needs 1 kg of boxwood and a large set needs 3 kg
    m.addCons(small_set + 3 * large_set <= boxwood_kg)

    # a small set yields a profit of $5 and a large set a profit of $20
    max_profit = 5 * small_set + 20 * large_set
    m.setObjective(max_profit, "maximize")

    return m, {
        "large_set": large_set,
        "max_profit": max_profit,
        "small_set": small_set,
    }

# Money change: Alice gives Bob an amount of change using her available coins,
# minimising the number of coins used. coin_counts[i] is the number of coins of
# type i given to Bob. Model in Python-MIP (CBC).
import mip


def build(instance):
    amount = instance["amount"]
    values = instance["types_of_coins"]
    available = instance["available_coins"]
    n = len(values)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # The number of coins of each type, between 0 and the number available.
    counts = [
        model.add_var(f"coins_{i}", lb=0, ub=available[i], var_type=mip.INTEGER)
        for i in range(n)
    ]

    # Alice has to give Bob some change: the change is composed with the
    # available coins so that its total value is the amount.
    model.add_constr(
        mip.xsum(values[i] * counts[i] for i in range(n)) == amount,
        "amount_given",
    )

    # Minimise the number of coins used.
    model.objective = mip.xsum(counts)

    return model, {"coin_counts": counts}

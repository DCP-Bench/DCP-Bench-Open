# Ages of the three sons of an old man (puzzle). Ages A1 >= A2 >= A3 (oldest first)
# are positive integers. Find the unique triple consistent with all clues.
import mip


def build(instance):
    product = 36
    # All multisets of three positive integers with product 36, ordered a >= b >= c.
    triples = []
    for a in range(1, product + 1):
        for b in range(1, a + 1):
            for c in range(1, b + 1):
                if a * b * c == product:
                    triples.append((a, b, c))
    max_age = max(max(t) for t in triples)
    max_sum = max(sum(t) for t in triples)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # The product of their ages is 36: one selector per candidate triple.
    pick = [model.add_var(f"pick_{k}", var_type=mip.BINARY) for k in range(len(triples))]
    model.add_constr(mip.xsum(pick) == 1)

    ages = [model.add_var(f"A{i + 1}", lb=1, ub=max_age, var_type=mip.INTEGER) for i in range(3)]
    for i in range(3):
        model.add_constr(
            ages[i] == mip.xsum(t[i] * pick[k] for k, t in enumerate(triples))
        )

    # The sum of their ages equals the number of windows in the building.
    # That number is unknown: a variable.
    windows = model.add_var("windows", lb=3, ub=max_sum, var_type=mip.INTEGER)
    model.add_constr(windows == ages[0] + ages[1] + ages[2])

    # Clue 2: "I need more information." The sum does not identify the triple, so
    # at least two triples of the product set have this same sum. Indicator w_k is 1
    # only when triple k has sum equal to the windows count (big-M from max_sum).
    same_sum = [model.add_var(f"same_sum_{k}", var_type=mip.BINARY) for k in range(len(triples))]
    big_m = max_sum
    for k, t in enumerate(triples):
        model.add_constr(windows - sum(t) <= big_m * (1 - same_sum[k]))
        model.add_constr(sum(t) - windows <= big_m * (1 - same_sum[k]))
    model.add_constr(mip.xsum(same_sum) >= 2)

    # Clue 3: "The oldest son has blue eyes. I got it." The oldest son is unique,
    # so A1 is strictly greater than A2.
    model.add_constr(ages[0] >= ages[1] + 1)

    return model, {"A1": ages[0], "A2": ages[1], "A3": ages[2]}

# Kidney exchange: n people on a waiting list. compatible[i] is the set of people
# that person i can donate a kidney to. Maximise the number of people who receive a
# kidney, where anyone who gives must receive one and nobody receives more than one.
# Output transplants[i][j] is 1 if person i donates to person j, else 0.
import mip


def build(instance):
    n = instance["num_people"]
    compatible = instance["compatible"]

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # Decision variables: one binary per compatible donor-recipient pair (i, j), i != j.
    x = {}
    for i in range(n):
        for j1 in compatible[i]:
            j = j1 - 1
            if j != i:
                x[(i, j)] = model.add_var(f"x_{i}_{j}", var_type=mip.BINARY)

    # Each person donates at most one kidney.
    # Donation capacity: each person donates to at most one recipient.
    for i in range(n):
        out_i = [x[(i, j)] for j in range(n) if (i, j) in x]
        if out_i:
            model.add_constr(mip.xsum(out_i) <= 1, f"donate_at_most_one_{i}")

    # Nobody receives more than one kidney.
    # Each person receives at most one kidney.
    for j in range(n):
        in_j = [x[(i, j)] for i in range(n) if (i, j) in x]
        if in_j:
            model.add_constr(mip.xsum(in_j) <= 1, f"receive_at_most_one_{j}")

    # Anyone who gives a kidney must receive one.
    # If person i donates, person i must also receive a kidney.
    for i in range(n):
        out_i = [x[(i, j)] for j in range(n) if (i, j) in x]
        in_i = [x[(k, i)] for k in range(n) if (k, i) in x]
        if out_i:
            model.add_constr(
                mip.xsum(out_i) <= mip.xsum(in_i), f"giver_receives_{i}"
            )

    # Objective: maximise the number of people who receive a kidney.
    model.objective = mip.xsum(x.values())

    # Output: transplants[i][j] is the binary donation variable, or 0 when the
    # pair is not compatible (or i == j).
    transplants = [
        [x[(i, j)] if (i, j) in x else 0 for j in range(n)] for i in range(n)
    ]

    return model, {"transplants": transplants}

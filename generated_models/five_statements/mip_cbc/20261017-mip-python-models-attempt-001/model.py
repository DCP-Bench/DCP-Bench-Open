# Five statements: decide which of five statements is true, where statement k says
# "Exactly k of these statements are false" (k = 1..5). Output statements[k-1] = 1 if statement k is true.
import mip


def build(instance):
    n = 5
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # statements[k-1] = 1 if statement k is true
    statements = [model.add_var(f"s_{k}", var_type=mip.BINARY) for k in range(1, n + 1)]

    # the number of false statements is F, which lies in 0..5
    # one-hot choice of F: count[j] = 1 if exactly j statements are false
    count = [model.add_var(f"count_{j}", var_type=mip.BINARY) for j in range(0, n + 1)]
    # exactly one count value holds
    model.add_constr(mip.xsum(count) == 1)

    # the number of false statements F is the sum over j of j times count[j]
    false_total = mip.xsum(j * count[j] for j in range(0, n + 1))

    # the number of true statements is 5 minus the number of false statements
    model.add_constr(mip.xsum(statements) == n - false_total)

    # statement k is true exactly when exactly k of the statements are false
    for k in range(1, n + 1):
        # statement k is true if and only if exactly k statements are false
        model.add_constr(statements[k - 1] == count[k])

    return model, {"statements": statements}

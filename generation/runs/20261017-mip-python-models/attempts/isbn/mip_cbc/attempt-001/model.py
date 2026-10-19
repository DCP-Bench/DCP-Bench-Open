# ISBN-13 validation and check digit calculation: fill in the unknown digits (-1 in isbn_init)
# of a 13-digit number so that it is a valid ISBN-13.
import mip


def build(instance):
    init = instance["isbn_init"]
    n = len(init)
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # the digits of the ISBN: a given digit is fixed to its value, an unknown digit (-1) is 0..9
    isbn = []
    for i, v in enumerate(init):
        if v >= 0:
            isbn.append(model.add_var(f"d{i}", lb=v, ub=v, var_type=mip.INTEGER))
        else:
            isbn.append(model.add_var(f"d{i}", lb=0, ub=9, var_type=mip.INTEGER))

    # the weights alternate 1 and 3, starting with 1
    weights = [1 if i % 2 == 0 else 3 for i in range(n)]

    # an ISBN-13 must start with 978 or 979: the first digit is 9, the second 7, the third 8 or 9
    model += isbn[0] == 9
    model += isbn[1] == 7
    model += isbn[2] >= 8

    # the check digit is (10 - (sum % 10)) % 10, which is the digit that makes the weighted
    # sum of all 13 digits a multiple of 10; so the weighted sum of all 13 digits is 10 * k
    max_total = 9 * sum(weights)
    k = model.add_var("k", lb=0, ub=max_total // 10, var_type=mip.INTEGER)
    model += mip.xsum(w * d for w, d in zip(weights, isbn)) == 10 * k

    return model, {"isbn": isbn}

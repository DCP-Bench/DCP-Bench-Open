# Problem divisible_by_1_through_9: find a 10 digit number that uses each of the digits 0 to 9
# exactly once and where the number formed by the first n digits of the number is divisible by n.
# The output is the number (number). Satisfaction problem; the instance carries no fields.
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Ten positions (0 is the leftmost digit) and ten digit values 0..9.
    # pick[i][v] = 1 when position i holds digit v; d[i] is that digit.
    pick = [[model.add_var(f"p_{i}_{v}", var_type=mip.BINARY) for v in range(10)] for i in range(10)]
    d = [model.add_var(f"d_{i}", lb=0, ub=9, var_type=mip.INTEGER) for i in range(10)]

    # each position takes exactly one digit
    for i in range(10):
        model.add_constr(mip.xsum(pick[i]) == 1)
        model.add_constr(d[i] == mip.xsum(v * pick[i][v] for v in range(10)))

    # each digit value is used exactly once
    for v in range(10):
        model.add_constr(mip.xsum(pick[i][v] for i in range(10)) == 1)

    # the number is a 10 digit number, so its leading digit is not 0
    model.add_constr(d[0] >= 1)

    # the number formed by the first n digits is divisible by n, for n = 1..10
    for n in range(1, 11):
        prefix = mip.xsum(10 ** (n - 1 - i) * d[i] for i in range(n))
        k = model.add_var(f"k_{n}", lb=0, ub=(10 ** n - 1) // n, var_type=mip.INTEGER)
        model.add_constr(prefix == n * k)

    # the number itself, read from the ten digits left to right
    number = model.add_var("number", lb=10 ** 9, ub=10 ** 10 - 1, var_type=mip.INTEGER)
    model.add_constr(number == mip.xsum(10 ** (9 - i) * d[i] for i in range(10)))

    return model, {"number": number}

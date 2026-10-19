# Problem: de Bruijn sequence de_bruijn of order n on an alphabet of size base.
# Output: a cyclic sequence of length base^n over the symbols 0..base-1, in which
# every possible length-n string occurs exactly once as a (cyclic) substring.
import mip


def build(instance):
    k = instance["base"]
    n = instance["n"]
    length = k ** n

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # the sequence: one integer symbol per position, in 0..base-1
    seq = [
        model.add_var(f"s_{i}", lb=0, ub=k - 1, var_type=mip.INTEGER)
        for i in range(length)
    ]

    # the word starting at position i (cyclic) read as a base-k number in 0..base^n-1
    # word_i = sum_j k^j * s_{(i+j) mod length}
    word = []
    for i in range(length):
        terms = [(k ** j) * seq[(i + j) % length] for j in range(n)]
        word.append(mip.xsum(terms))

    # every length-n string occurs exactly once: the length windows take
    # all length base^n values, each value used by exactly one window.
    # one-hot per window, value v in 0..base^n-1
    onehot = [
        [model.add_var(f"w_{i}_{v}", var_type=mip.BINARY) for v in range(length)]
        for i in range(length)
    ]

    # each window takes exactly one string value
    for i in range(length):
        # the window is a string: its value is the one-hot value
        model.add_constr(mip.xsum(onehot[i]) == 1, name=f"one_value_{i}")
        model.add_constr(
            mip.xsum(v * onehot[i][v] for v in range(length)) == word[i],
            name=f"window_value_{i}",
        )

    # each string value occurs in at most one window (so exactly one, by counting)
    for v in range(length):
        model.add_constr(
            mip.xsum(onehot[i][v] for i in range(length)) <= 1,
            name=f"string_once_{v}",
        )

    return model, {"de_bruijn": seq}

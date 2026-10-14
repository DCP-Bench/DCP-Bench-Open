# Five statements (Joyner): statement i says "exactly i of these statements are false",
# for i = 1..5. Determine which statements are true.
import functools
import itertools
import operator

from hermax.model import Model


def define(m, inputs, function):
    """A new literal that equals function(*inputs) for 0/1 inputs, as clauses."""
    out = m.bool()
    for values in itertools.product((0, 1), repeat=len(inputs)):
        clause = [~lit if value else lit for lit, value in zip(inputs, values)]
        clause.append(out if function(*values) else ~out)
        m &= functools.reduce(operator.or_, clause)
    return out


def build(instance):
    # The statements are fixed by the problem; the instance carries no data.
    n = 5

    m = Model()
    # statements[i] = statement i + 1 is true
    statements = m.bool_vector("statements", n)
    true = m.bool("true")
    m &= true

    # Count the false statements in unary with a sequential counter:
    # at_least[j][k] = at least k of the first j statements are false.
    at_least = [[true] + [~true] * (n + 1)]
    for j in range(n):
        row = [true]
        for k in range(1, n + 2):
            # at least k among the first j + 1: at least k among the first j, or at least
            # k - 1 among them and statement j + 1 false
            row.append(define(m, [at_least[j][k], at_least[j][k - 1], statements[j]],
                              lambda a, b, s: a | (b & (1 - s))))
        at_least.append(row)
    count = at_least[n]

    # Statement i is true exactly when exactly i of the statements are false: at least i
    # and not at least i + 1.
    for i in range(1, n + 1):
        m &= (~statements[i - 1] | count[i])
        m &= (~statements[i - 1] | ~count[i + 1])
        m &= (statements[i - 1] | ~count[i] | count[i + 1])

    return m, {"statements": statements}

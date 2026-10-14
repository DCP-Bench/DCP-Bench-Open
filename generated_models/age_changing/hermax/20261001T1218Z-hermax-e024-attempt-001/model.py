# Age changing: start with my age and apply the four operations +2, /8, -3 and *7 once
# each, in some order; the result is my husband's age. Starting from his age and applying
# the same four operations in a different order gives my age. Find both ages (both between
# 16 and 120).
import functools
import operator

from hermax.model import Model


def clause(lits):
    """The disjunction of the given literals."""
    return functools.reduce(operator.or_, lits)


def exactly_one(m, lits, name):
    """Post "exactly one of lits is true" with a ladder encoding.

    prefix[i] says that one of lits[0..i] is true; each literal sets its prefix,
    prefixes carry on, and a literal after a set prefix is forbidden. That takes
    three clauses per literal, where forbidding every pair takes a quadratic number.
    """
    prefix = m.bool_vector(name, len(lits))
    for i, lit in enumerate(lits):
        m &= (~lit | prefix[i])
        if i + 1 < len(lits):
            m &= (~prefix[i] | prefix[i + 1])
            m &= (~lits[i + 1] | ~prefix[i])
    m &= clause(lits)


# The four operations, as the function from the age before to the age after, or None where
# the result is not a whole number. "/8" means the new age times 8 is the old age, as in
# the reference. These belong to the puzzle, not to an instance.
OPERATIONS = [
    lambda old: old + 2,
    lambda old: old // 8 if old % 8 == 0 else None,
    lambda old: old - 3,
    lambda old: old * 7,
]


def post_step(m, gate, old, new, operation):
    """Post: when the literal `gate` holds, new == operation(old).

    hermax integers use an order encoding, with the literal (x >= k). For every value v of
    `old`, "old is v" (old >= v and not old >= v + 1) forces new to operation(v), or is
    impossible when that is not a whole number or falls outside the range of new.
    """
    for v in range(old.lb, old.ub + 1):
        guard = [~gate]
        if v > old.lb:
            guard.append(~(old >= v))
        if v < old.ub:
            guard.append(old >= v + 1)
        w = operation(v)
        if w is None or not new.lb <= w <= new.ub:
            m &= clause(guard)
        else:
            if w > new.lb:
                m &= clause(guard + [new >= w])
            if w < new.ub:
                m &= clause(guard + [~(new >= w + 1)])


def build(instance):
    # This puzzle has no instance data: the ages' range, the four operations and the number
    # of them are part of the problem itself, so they are written here as constants.
    n = 4  # number of operations
    age_low, age_high = 16, 120  # the ages are between 16 and 120
    value_high = 1000  # the reference's range for the ages in the middle of a chain

    m = Model()
    # m_age = my age, h_age = my husband's age (the declared outputs m and h)
    m_age = m.int("m", age_low, age_high)
    h_age = m.int("h", age_low, age_high)
    # h_list[i] = the age after i operations when starting from my age; it ends at my
    # husband's age. m_list[i] = the same starting from his age; it ends at mine.
    # The two ends are the ages themselves, and the ages between them are whole numbers
    # from 1 to 1000.
    h_list = [m_age] + [m.int(f"h_list_{i}", 1, value_high) for i in range(1, n)] + [h_age]
    m_list = [h_age] + [m.int(f"m_list_{i}", 1, value_high) for i in range(1, n)] + [m_age]

    # perm1[i][k] = the i-th operation applied to my age is operation k;
    # perm2[i][k] = the i-th operation applied to his age is operation k
    perm1 = [m.bool_vector(f"perm1_{i}", n) for i in range(n)]
    perm2 = [m.bool_vector(f"perm2_{i}", n) for i in range(n)]

    # each order uses every operation once: one operation per place, and each operation in
    # exactly one place
    for perm, tag in ((perm1, "perm1"), (perm2, "perm2")):
        for i in range(n):
            exactly_one(m, [perm[i][k] for k in range(n)], f"{tag}_place_{i}")
        for k in range(n):
            exactly_one(m, [perm[i][k] for i in range(n)], f"{tag}_operation_{k}")

    # the two orders are different: in some place the operations differ (a flag per
    # (place, operation) that can only be on if exactly one of the two orders uses it there)
    differ = []
    for i in range(n):
        for k in range(n):
            flag = m.bool()
            m &= (~flag | perm1[i][k] | perm2[i][k])
            m &= (~flag | ~perm1[i][k] | ~perm2[i][k])
            differ.append(flag)
    m &= clause(differ)

    # applying the operations in the order perm1 to my age gives h_list, and in the order
    # perm2 to his age gives m_list
    for i in range(n):
        for k in range(n):
            post_step(m, perm1[i][k], h_list[i], h_list[i + 1], OPERATIONS[k])
            post_step(m, perm2[i][k], m_list[i], m_list[i + 1], OPERATIONS[k])

    return m, {"m": m_age, "h": h_age}

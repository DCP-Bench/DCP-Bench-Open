# Handshaking: Hilary and Jocelyn, a couple, invite some other couples. Nobody
# shakes hands with themselves or their spouse, and everybody except Hilary
# reports a different number of handshakes. How many hands did Hilary shake?
from hermax.model import Model


def build(instance):
    num_couples = instance["num_couples"]  # couples invited, Hilary and Jocelyn not counted
    n = 2 + num_couples * 2  # people; couples sit at (0, 1), (2, 3), ...; Hilary is 0, Jocelyn 1

    m = Model()
    # x[i] = number of hands person i shook; nobody can shake more than n - 2
    # (not themselves, not their spouse)
    x = m.int_vector("x", n, 0, n - 2)
    hil = x[0]  # Hilary

    # shook[(i, j)] = persons i < j shook hands. A handshake is mutual, so one
    # variable per pair covers both directions; spouses never shake hands.
    shook = {(i, j): m.bool(f"shook_{i}_{j}")
             for i in range(n) for j in range(i + 1, n) if j != i ^ 1}

    def partners(i):
        return [shook[(min(i, j), max(i, j))] for j in range(n) if j != i and j != i ^ 1]

    # x[i] counts the handshakes of person i
    for i in range(n):
        m &= (sum(partners(i)) == x[i])

    # everybody except Hilary shook a different number of hands
    for i in range(1, n):
        for j in range(i + 1, n):
            m &= (x[i] != x[j])

    # Symmetry breaking among the invited couples (persons 2 .. n - 1). The guests
    # of a couple are interchangeable, and so are the couples, so any solution
    # stays a solution after swapping the two spouses of a couple or exchanging
    # two couples. Fix one representative: within a couple the first spouse has
    # the smaller count (their counts are different), and the couples are listed
    # by the count of their first spouse. Hilary and Jocelyn are not moved, and
    # Hilary's count is the same in every swapped solution, so hil is unchanged.
    for c in range(1, num_couples + 1):
        m &= (x[2 * c] < x[2 * c + 1])
        if c < num_couples:
            m &= (x[2 * c] < x[2 * c + 2])

    return m, {"hil": hil}

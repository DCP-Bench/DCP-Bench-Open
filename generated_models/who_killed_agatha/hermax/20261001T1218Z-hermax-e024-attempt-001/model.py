# Who killed Agatha: someone in Dreadsbury Mansion killed Aunt Agatha. From what is known
# about who hates whom and who is richer than whom, find the killer.
from hermax.model import Model

# The residents in the order the problem lists them: Agatha, the butler, Charles.
AGATHA, BUTLER, CHARLES = range(3)


def build(instance):
    n = len(instance["names"])  # the people living in the mansion
    victim = AGATHA

    m = Model()
    # killer = index of the killer (0 Agatha, 1 the butler, 2 Charles)
    killer = m.int("killer", 0, n - 1)
    # hates[i][j] = i hates j; richer[i][j] = i is richer than j
    hates = m.bool_matrix("hates", n, n)
    richer = m.bool_matrix("richer", n, n)

    # A killer always hates, and is no richer than, his victim.
    for k in range(n):
        m &= (~(killer == k) | hates[k][victim])
        m &= (~(killer == k) | ~richer[k][victim])

    # No one is richer than himself, and of two different people exactly one is richer.
    for i in range(n):
        m &= ~richer[i][i]
        for j in range(i + 1, n):
            m &= (richer[i][j] | richer[j][i])
            m &= (~richer[i][j] | ~richer[j][i])

    # Charles hates no one that Agatha hates.
    for i in range(n):
        m &= (~hates[AGATHA][i] | ~hates[CHARLES][i])

    # Agatha hates everybody except the butler.
    m &= hates[AGATHA][AGATHA]
    m &= hates[AGATHA][CHARLES]
    m &= ~hates[AGATHA][BUTLER]

    # The butler hates everyone not richer than Aunt Agatha.
    for i in range(n):
        m &= (richer[i][AGATHA] | hates[BUTLER][i])

    # The butler hates everyone whom Agatha hates.
    for i in range(n):
        m &= (~hates[AGATHA][i] | hates[BUTLER][i])

    # No one hates everyone.
    for i in range(n):
        m &= (sum(hates[i][j] for j in range(n)) <= n - 1)

    return m, {"killer": killer}

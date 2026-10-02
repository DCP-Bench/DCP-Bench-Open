# Who killed Agatha: Agatha, the butler and Charles are the only people in Dreadsbury Mansion,
# and one of them killed Agatha. A killer always hates, and is no richer than, the victim.
# Hatred and wealth obey the clues below. Who is the killer?
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = len(instance["names"])  # the people of the mansion
    agatha, butler, charles = 0, 1, 2  # their positions in the list of names
    victim = agatha

    pool = IDPool()
    # killer = the person who killed Agatha (0 = Agatha herself, 1 = the butler, 2 = Charles)
    killer = Integer("killer", 0, n - 1, vpool=pool)
    engine = IntegerEngine(vars=[killer], vpool=pool)
    cnf = engine.clausify()

    # hates[i][j] is true when person i hates person j
    hates = [[pool.id(("hates", i, j)) for j in range(n)] for i in range(n)]
    # richer[i][j] is true when person i is richer than person j
    richer = [[pool.id(("richer", i, j)) for j in range(n)] for i in range(n)]

    # A killer always hates, and is no richer than, his victim.
    for person in range(n):
        cnf.append([-killer.equals(person), hates[person][victim]])
        cnf.append([-killer.equals(person), -richer[person][victim]])

    # Nobody is richer than himself, and of two different people exactly one is richer.
    for i in range(n):
        cnf.append([-richer[i][i]])
        for j in range(i + 1, n):
            cnf.append([richer[i][j], richer[j][i]])
            cnf.append([-richer[i][j], -richer[j][i]])

    # Charles hates nobody that Agatha hates.
    for i in range(n):
        cnf.append([-hates[agatha][i], -hates[charles][i]])

    # Agatha hates everybody except the butler.
    for i in range(n):
        cnf.append([-hates[agatha][i] if i == butler else hates[agatha][i]])

    # The butler hates everyone not richer than Aunt Agatha.
    for i in range(n):
        cnf.append([richer[i][agatha], hates[butler][i]])

    # The butler hates everyone whom Agatha hates.
    for i in range(n):
        cnf.append([-hates[agatha][i], hates[butler][i]])

    # Nobody hates everyone: each person hates at most n - 1 people.
    for i in range(n):
        cnf.extend(CardEnc.atmost(lits=hates[i], bound=n - 1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    return cnf, {"killer": killer}

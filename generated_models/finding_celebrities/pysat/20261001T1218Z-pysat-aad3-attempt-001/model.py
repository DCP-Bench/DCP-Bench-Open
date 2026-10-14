# Finding celebrities: from who knows whom at a party, find the celebrities. A celebrity is
# known by everybody (including the celebrity, by the diagonal convention of the data) and
# knows only celebrities, so a celebrity knows exactly as many people as there are
# celebrities. At least one celebrity is present.
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def build(instance):
    graph = instance["graph"]  # graph[i][j] = 1 when person i knows person j
    n = len(graph)

    pool = IDPool()
    cnf = CNF()
    # celebrity[i] is true when person i is a celebrity
    celebrity = [pool.id(("celebrity", i)) for i in range(n)]
    # count_is[k] is true when there are exactly k celebrities (between 1 and n)
    count_is = {k: pool.id(("count", k)) for k in range(1, n + 1)}

    # exactly one value of the number of celebrities holds
    cnf.extend(CardEnc.equals(lits=list(count_is.values()), bound=1, vpool=pool,
                              encoding=EncType.pairwise).clauses)

    # count_is[k] fixes the number of celebrities to k. Every clause of the cardinality
    # encoding gets the guard "not count_is[k]", so it only binds when count_is[k] holds
    # (its auxiliary variables are fresh, so they are free otherwise).
    for k, selector in count_is.items():
        for clause in CardEnc.equals(lits=celebrity, bound=k, vpool=pool, encoding=EncType.seqcounter).clauses:
            cnf.append([-selector] + clause)

    # A person is a celebrity exactly when everybody knows them and they know exactly as many
    # people as there are celebrities. The data are fixed, so "everybody knows i" and "i knows
    # r people" are known when the model is built.
    for i in range(n):
        known_by_everybody = sum(graph[j][i] for j in range(n)) == n
        knows = sum(graph[i][j] for j in range(n))
        if known_by_everybody and 1 <= knows <= n:
            cnf.append([-celebrity[i], count_is[knows]])
            cnf.append([celebrity[i], -count_is[knows]])
        else:
            cnf.append([-celebrity[i]])

    return cnf, {"celebrities": celebrity}

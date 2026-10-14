# Social golfers: n_groups * group_size golfers play once a week for n_weeks weeks, in
# groups of group_size, such that no two golfers are in the same group more than once.
from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n_weeks = instance["n_weeks"]
    n_groups = instance["n_groups"]
    group_size = instance["group_size"]
    n_golfers = n_groups * group_size

    pool = IDPool()
    # assign[g][w] = the group (0-indexed) that golfer g plays in during week w.
    # The direct encoding gives a literal assign[g][w].equals(k) for "golfer g is in
    # group k in week w", and exactly one of them is true.
    assign = [[Integer(f"assign{g}_{w}", 0, n_groups - 1, vpool=pool) for w in range(n_weeks)]
              for g in range(n_golfers)]
    engine = IntegerEngine(vars=[a for row in assign for a in row], vpool=pool)
    cnf = engine.clausify()
    in_group = [[[assign[g][w].equals(k) for k in range(n_groups)] for w in range(n_weeks)]
                for g in range(n_golfers)]

    # each group has exactly group_size players in every week
    for w in range(n_weeks):
        for k in range(n_groups):
            cnf.extend(CardEnc.equals(lits=[in_group[g][w][k] for g in range(n_golfers)],
                                      bound=group_size, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # each pair of golfers meets (is in the same group) in at most one week.
    # meet[g1,g2,w] must be true whenever both golfers are in one group in week w;
    # it is only forced upwards, which is enough because it is then limited to one week.
    for g1, g2 in combinations(range(n_golfers), 2):
        meet = []
        for w in range(n_weeks):
            flag = pool.id(("meet", g1, g2, w))
            for k in range(n_groups):
                cnf.append([-in_group[g1][w][k], -in_group[g2][w][k], flag])
            meet.append(flag)
        cnf.extend(CardEnc.atmost(lits=meet, bound=1, vpool=pool,
                                  encoding=EncType.pairwise).clauses)

    return cnf, {"assign": assign}

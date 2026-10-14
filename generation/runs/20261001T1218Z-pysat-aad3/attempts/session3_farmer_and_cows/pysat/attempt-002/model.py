# Farmer and cows: cow number i gives i units of milk. Share the cows among the sons so that
# each son receives the prescribed number of cows and all sons get the same total quantity of milk.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc, EncType as PBEncType


def build(instance):
    num_cows = instance["num_cows"]
    num_sons = instance["num_sons"]
    cows_per_son = instance["cows_per_son"]  # how many cows each son gets

    milk_per_cow = list(range(1, num_cows + 1))          # cow i gives i units of milk
    milk_per_son = sum(milk_per_cow) // num_sons         # every son's share of the milk

    pool = IDPool()
    # cow_assignments[i] = the son (0..num_sons-1) who receives cow i + 1
    cow_assignments = [Integer(f"cow{i}", 0, num_sons - 1, vpool=pool) for i in range(num_cows)]
    engine = IntegerEngine(vars=cow_assignments, vpool=pool)
    cnf = engine.clausify()

    # gets[son][i] is true when cow i + 1 goes to that son
    gets = [[cow.equals(son) for cow in cow_assignments] for son in range(num_sons)]

    for son in range(num_sons):
        # each son gets the prescribed number of cows
        cnf.extend(CardEnc.equals(lits=gets[son], bound=cows_per_son[son], vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

        # every son gets the same total quantity of milk (a BDD encoding keeps the propagation
        # strong, which matters for this kind of equal-sum partition)
        cnf.extend(PBEnc.equals(lits=gets[son], weights=milk_per_cow, bound=milk_per_son, vpool=pool,
                                encoding=PBEncType.bdd).clauses)

    # Symmetry breaking. Two neighbouring sons who must receive the same number of cows are
    # interchangeable (they also get the same milk), so any solution can be renamed so that the
    # lowest-numbered cow of the first of them comes before the lowest-numbered cow of the second.
    # This only chooses one labelling per solution; the declared output keeps its meaning.
    # started[son][i] is true only if one of the cows 1..i + 1 goes to that son.
    started = [[pool.id(("started", son, i)) for i in range(num_cows)] for son in range(num_sons)]
    for son in range(num_sons):
        cnf.append([-started[son][0], gets[son][0]])
        for i in range(1, num_cows):
            cnf.append([-started[son][i], started[son][i - 1], gets[son][i]])
    for son in range(num_sons - 1):
        if cows_per_son[son] == cows_per_son[son + 1]:
            # the next son can only take cow i after the previous son has taken an earlier cow
            cnf.append([-gets[son + 1][0]])
            for i in range(1, num_cows):
                cnf.append([-gets[son + 1][i], started[son][i - 1]])

    return cnf, {"cow_assignments": cow_assignments}

# Farmer and cows: cow number i gives i units of milk. Share the cows among the sons so that
# each son receives the prescribed number of cows and all sons get the same total quantity of milk.
from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


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

    for son in range(num_sons):
        # gets[i] is true when cow i + 1 goes to this son
        gets = [cow.equals(son) for cow in cow_assignments]

        # each son gets the prescribed number of cows
        cnf.extend(CardEnc.equals(lits=gets, bound=cows_per_son[son], vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

        # every son gets the same total quantity of milk
        cnf.extend(PBEnc.equals(lits=gets, weights=milk_per_cow, bound=milk_per_son, vpool=pool).clauses)

    return cnf, {"cow_assignments": cow_assignments}

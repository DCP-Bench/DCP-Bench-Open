# Match four pairs of shoes to the four stops they were bought at.
# The clues are the puzzle, so the instance carries no fields.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = 4
    pool = IDPool()
    shoes = [Integer(f"shoe{i}", 1, n, vpool=pool) for i in range(n)]
    store = [Integer(f"store{i}", 1, n, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=shoes + store, vpool=pool)
    engine.add_alldifferent(shoes)
    engine.add_alldifferent(store)

    ecru, fuchsia, purple, suede = shoes
    footfarm, heels, palace, tootsies = store

    # 1. fuchsia flats came from Heels in a Handcart
    engine.add_equal(fuchsia, heels)
    # 4. the suede sandals came two stops after The Shoe Palace
    engine.add_linear(palace - suede == -2)
    cnf = engine.clausify()

    # 2. the stop after the purple pumps was not Tootsies
    for v in range(1, n):
        cnf.append([-purple.equals(v), -tootsies.equals(v + 1)])
    # 3. the Foot Farm was the second stop
    cnf.append([footfarm.equals(2)])

    return cnf, {"ecruespadrilles": ecru, "fuchsiaflats": fuchsia,
                 "purplepumps": purple, "suedesandals": suede,
                 "footfarm": footfarm, "heelsinahandcart": heels,
                 "theshoepalace": palace, "tootsies": tootsies}

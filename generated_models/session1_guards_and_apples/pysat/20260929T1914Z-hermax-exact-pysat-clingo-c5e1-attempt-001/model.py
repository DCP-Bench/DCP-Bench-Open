# Guards and apples: a boy passes several gates. At each gate he gives the guard
# half of his apples plus one, and after the last gate one apple is left for the girl.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    num_gates = instance["num_gates"]

    pool = IDPool()
    # apples[i] = the apples the boy has before gate i; the last entry is what he has
    # after the last gate. The apples are between 0 and 100.
    apples = [Integer(f"apples_{i}", 0, 100, vpool=pool) for i in range(num_gates + 1)]
    engine = IntegerEngine(vars=apples, vpool=pool)

    # at each gate the guard gets half of the apples plus one, so the boy is left
    # with half of them minus one: before = 2 * (after + 1)
    for i in range(1, num_gates + 1):
        engine.add_linear(apples[i - 1] == 2 * apples[i] + 2)
    cnf = engine.clausify()

    # after the last gate the boy keeps the one apple he gives to the girl
    cnf.append([apples[num_gates].equals(1)])

    return cnf, {"apples": apples}

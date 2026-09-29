# Devil's word: put a plus or minus sign in front of every number of a list so
# that the signed numbers add up to the given total.
from pysat.formula import CNF, IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    arr = instance["arr"]  # the numbers, in order
    total = instance["total"]  # the sum the signed numbers must reach
    n = len(arr)

    pool = IDPool()
    # plus[i] is true when arr[i] is added and false when it is subtracted
    plus = [pool.id(("plus", i)) for i in range(n)]
    # result[i] = arr[i] with its chosen sign, an integer in -arr[i]..arr[i]
    result = [Integer(f"result_{i}", -abs(arr[i]), abs(arr[i]), vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=result, vpool=pool)
    cnf = engine.clausify()
    for i in range(n):
        cnf.append([-plus[i], result[i].equals(arr[i])])
        cnf.append([plus[i], result[i].equals(-arr[i])])

    # The signed numbers add up to the total. Over the sign literals this is
    # sum(arr) - 2 * (what is subtracted) = total, which is the pseudo-Boolean
    # constraint 2 * sum(arr[i] * plus[i]) = total + sum(arr).
    cnf.extend(PBEnc.equals(lits=plus, weights=[2 * value for value in arr],
                            bound=total + sum(arr), vpool=pool).clauses)

    return cnf, {"result": result}

# Curious set of integers (Martin Gardner): the integers 1, 3, 8 and 120 have the property that
# the product of any two of them is one less than a perfect square. Find a fifth number, at
# least 0, that can be added to the set without destroying this property.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]              # size of the set once the new number is added
    max_val = instance["max_val"]  # every number, and every square root below, lies in 0..max_val
    members = [1, 3, 8, 120]       # the integers of the set, given by the problem statement
    assert n == len(members) + 1, "the problem adds exactly one number to the four given ones"

    pool = IDPool()
    # number = the new member of the set
    number = Integer("number", 0, max_val, vpool=pool)
    # root[member] = the square root p, with p * p == member * number + 1
    root = {member: Integer(f"root{member}", 0, max_val, vpool=pool) for member in members}
    engine = IntegerEngine(vars=[number] + list(root.values()), vpool=pool)
    cnf = engine.clausify()

    # the new number is different from the numbers already in the set
    for member in members:
        if member <= max_val:
            cnf.append([-number.equals(member)])

    # The product of the new number with each member, plus one, is a perfect square p * p, with
    # p in 0..max_val. (The products of two given members are not repeated here: they are
    # fixed numbers, and the problem states that they have the property.)
    # PySAT cannot multiply two variables, so both sides are tabulated. value_is[v] stands for
    # "the common value is v": every value of p forces the literal of p * p, every value of the
    # new number forces the literal of member * number + 1, and at most one literal may hold, so
    # the two have to agree.
    for member in members:
        value_is = {}
        for p in range(max_val + 1):
            if p * p not in value_is:
                value_is[p * p] = pool.id(("value", member, p * p))
            cnf.append([-root[member].equals(p), value_is[p * p]])
        for w in range(max_val + 1):
            if member * w + 1 not in value_is:
                value_is[member * w + 1] = pool.id(("value", member, member * w + 1))
            cnf.append([-number.equals(w), value_is[member * w + 1]])
        cnf.extend(CardEnc.atmost(lits=list(value_is.values()), bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    return cnf, {"number": number}

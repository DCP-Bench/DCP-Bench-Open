# Traffic lights: a four-way junction has four vehicle lights V1..V4 and four
# pedestrian lights P1..P4. Pick a state for each so that every pair of
# neighbouring roads shows one of the safe combinations.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # safe combinations of (V_i, P_i, V_{i+1}, P_{i+1}); everything else is forbidden
    allowed_tuples = instance["allowed_tuples"]

    pool = IDPool()
    # vehicle lights: 0 = red, 1 = red-yellow, 2 = green, 3 = yellow
    vehicle = [Integer(f"V{i + 1}", 0, 3, vpool=pool) for i in range(4)]
    # pedestrian lights: 0 = red, 1 = green
    pedestrian = [Integer(f"P{i + 1}", 0, 1, vpool=pool) for i in range(4)]
    engine = IntegerEngine(vars=vehicle + pedestrian, vpool=pool)
    cnf = engine.clausify()

    # each road and the next one (road 4 is followed by road 1) must show a safe
    # combination: exactly one allowed tuple is selected, and the four lights take
    # that tuple's values
    for i in range(4):
        nxt = (i + 1) % 4
        lights = [vehicle[i], pedestrian[i], vehicle[nxt], pedestrian[nxt]]
        selected = [pool.id(("road", i, "tuple", k)) for k in range(len(allowed_tuples))]
        cnf.extend(CardEnc.equals(lits=selected, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)
        for k, row in enumerate(allowed_tuples):
            for light, value in zip(lights, row):
                cnf.append([-selected[k], light.equals(value)])

    # reported in the order V1, V2, V3, V4, P1, P2, P3, P4
    return cnf, {"lights": vehicle + pedestrian}

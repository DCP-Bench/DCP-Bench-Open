from dd.autoref import BDD
import json

# Integers 0..100 as 8-bit unsigned values; arithmetic uses 12-bit registers.
VAR_BITS = 8
WIDTH = 12
bdd = BDD()
bdd.declare(*[f"{p}{i}" for p in "mwc" for i in range(VAR_BITS)])


def var_bits(prefix):
    bits = [bdd.var(f"{prefix}{i}") for i in range(VAR_BITS)]
    return bits + [bdd.false] * (WIDTH - VAR_BITS)


def const_bits(n):
    return [bdd.true if (n >> i) & 1 else bdd.false for i in range(WIDTH)]


def xor_bits(a, b):
    return (a | b) & ~(a & b)


def add_bvs(a, b):
    sums = []
    carry = bdd.false
    for x, y in zip(a, b):
        sums.append(xor_bits(xor_bits(x, y), carry))
        carry = (x & y) | (x & carry) | (y & carry)
    return sums


def eq_bvs(a, b):
    node = bdd.true
    for x, y in zip(a, b):
        node &= ~xor_bits(x, y)
    return node


def ule_bvs(a, b):
    acc_eq = bdd.true
    result = bdd.false
    for x, y in reversed(list(zip(a, b))):
        result |= acc_eq & ~x & y
        acc_eq &= ~xor_bits(x, y)
    return result | acc_eq


def shl(bits, k):
    return [bdd.false] * k + bits[: WIDTH - k]


men, women, children = var_bits("m"), var_bits("w"), var_bits("c")
hundred, two_hundred = const_bits(100), const_bits(200)

# 0..100 bounds
node = ule_bvs(men, hundred) & ule_bvs(women, hundred) & ule_bvs(children, hundred)
# 100 people in total
node &= eq_bvs(add_bvs(add_bvs(men, women), children), hundred)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
six_men = add_bvs(shl(men, 1), shl(men, 2))  # 2m + 4m
four_women = shl(women, 2)
node &= eq_bvs(add_bvs(add_bvs(six_men, four_women), children), two_hundred)
# Five times as many women as men: 4m + m
node &= eq_bvs(women, add_bvs(shl(men, 2), men))

picked = next(bdd.pick_iter(node), None)
if picked is None:
    raise SystemExit("No solution found.")


def value(prefix):
    return sum((1 << i) for i in range(VAR_BITS) if picked.get(f"{prefix}{i}", False))


print(json.dumps({
    "men": value("m"),
    "women": value("w"),
    "children": value("c"),
}))

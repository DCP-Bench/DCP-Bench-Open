from pysat.formula import IDPool
from pysat.pb import PBEnc
from pysdd.sdd import SddManager
import json

# Integers 0..100 as 8-bit unsigned values (binary encoding).
NBITS = 8
WEIGHTS = [2 ** i for i in range(NBITS)]
vpool = IDPool()


def bits(name):
    return [vpool.id(f"{name}_{i}") for i in range(NBITS)]


def value(bit_ids, model):
    return sum(w for w, lit in zip(WEIGHTS, bit_ids) if model.get(lit, 0))


# Decision variables: number of men, women, and children
men, women, children = bits("men"), bits("women"), bits("children")
clauses = []
for var in (men, women, children):
    clauses.extend(PBEnc.atmost(lits=var, weights=WEIGHTS, bound=100, vpool=vpool).clauses)

# 100 people in total
clauses.extend(PBEnc.equals(
    lits=men + women + children, weights=WEIGHTS * 3, bound=100, vpool=vpool,
).clauses)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
clauses.extend(PBEnc.equals(
    lits=men + women + children,
    weights=[6 * w for w in WEIGHTS] + [4 * w for w in WEIGHTS] + WEIGHTS,
    bound=200, vpool=vpool,
).clauses)
# Five times as many women as men
clauses.extend(PBEnc.equals(
    lits=women + men, weights=WEIGHTS + [-5 * w for w in WEIGHTS], bound=0, vpool=vpool,
).clauses)

dimacs = f"p cnf {vpool.top} {len(clauses)}\n"
dimacs += "".join(" ".join(str(lit) for lit in clause) + " 0\n" for clause in clauses)
mgr, alpha = SddManager.from_cnf_string(dimacs)
if alpha is None or alpha.is_false():
    raise SystemExit("No solution found.")
model = next(alpha.models())
print(json.dumps({
    "men": value(men, model),
    "women": value(women, model),
    "children": value(children, model),
}))

import json
import sys

import mip

data = json.load(open(sys.argv[1]))
addends = data["addends"]
total = data["sum"]
words = addends + [total]
letters = sorted(set("".join(words)))
leading = {w[0] for w in words if len(w) > 1}

m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
m.verbose = 0
m.max_mip_gap = 0.0
m.max_mip_gap_abs = 0.0
# p[l][v] = 1 when letter l stands for digit v (one-hot)
p = {l: {v: m.add_var(f"p_{l}_{v}", var_type=mip.BINARY) for v in range(10)} for l in letters}

# each letter gets exactly one digit
for l in letters:
    m += mip.xsum(p[l].values()) == 1

# different letters get different digits
for v in range(10):
    m += mip.xsum(p[l][v] for l in letters) <= 1

# no leading zero in a word of more than one letter
for l in leading:
    m += p[l][0] == 0


def weighted_terms(word):
    # the word as a number: each letter contributes digit * 10^position
    terms = []
    for k, ch in enumerate(reversed(word)):
        for v in range(1, 10):
            terms.append((10 ** k * v) * p[ch][v])
    return terms


# sum of the addends equals the sum word
m += mip.xsum(t for word in addends for t in weighted_terms(word)) == mip.xsum(weighted_terms(total))

m.objective = mip.xsum([])  # no objective: any solution is optimal

status = m.optimize(max_seconds=60)
if status == mip.OptimizationStatus.OPTIMAL:
    digits = {l: next(v for v in range(10) if p[l][v].x > 0.5) for l in letters}
    print(json.dumps({"digits": digits}))
elif status == mip.OptimizationStatus.INFEASIBLE:
    print(json.dumps({"status": "unsatisfiable"}))
else:
    raise SystemExit(f"Status: {status.name}")

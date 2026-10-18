# coin3_application: find the minimum number of coins that allows one to pay exactly
# any amount smaller than a given maximum amount, using a given set of denominations.
# Output x[k] is the number of coins of denomination k.
#
# Encoding: pay[k][a] is true when amount a can be paid exactly with coins of the first
# k+1 denominations, using at most x[j] coins of each denomination j. Only the implication
# pay[k][a] -> OR_c (x[k] >= c and pay[k-1][a - c*den[k]]) is needed, because every amount
# below the maximum has to be payable. The order literals ge[k][c] tie the coin counts to x.

import cvc5.pythonic as cz


def conj(parts):
    # Conjunction of Python bools and expressions, folding the constants away.
    out = []
    for p in parts:
        if p is False:
            return False
        if p is True:
            continue
        out.append(p)
    if not out:
        return True
    return out[0] if len(out) == 1 else cz.And(out)


def build(instance):
    den = instance["denominations"]
    top = instance["max_amount_to_pay"]
    nd = len(den)

    s = cz.SolverFor("QF_LIA")

    x = [cz.Int(f"x_{k}") for k in range(nd)]
    # Find the minimum number of coins, using a given set of denominations: the number of
    # coins of each denomination is a count from 0 up to what the largest amount to pay
    # (top - 1) can use of it.
    cap = [(top - 1) // den[k] for k in range(nd)]
    for k in range(nd):
        s.add(x[k] >= 0)
        s.add(x[k] <= cap[k])

    # ge[k][c] is true exactly when x[k] >= c (order encoding of the coin count).
    ge = []
    for k in range(nd):
        row = [True]
        for c in range(1, cap[k] + 1):
            b = cz.Bool(f"ge_{k}_{c}")
            s.add(cz.Implies(b, x[k] >= c))
            s.add(cz.Implies(x[k] >= c, b))
            if c > 1:
                s.add(cz.Implies(b, row[c - 1]))
            row.append(b)
        ge.append(row)

    # Pay exactly any amount smaller than a given maximum amount, using a given set of
    # denominations: layer by layer over the denominations. Amount 0 is always payable
    # (no coins), and with no denominations only amount 0 is payable.
    prev = [a == 0 for a in range(top)]
    for k in range(nd):
        last = k == nd - 1
        cur = [True]
        for a in range(1, top):
            opts = []
            trivially_true = False
            for c in range(0, min(cap[k], a // den[k]) + 1):
                lit = conj([ge[k][c], prev[a - c * den[k]]])
                if lit is True:
                    trivially_true = True
                    break
                if lit is not False:
                    opts.append(lit)
            if trivially_true:
                cur.append(True)
                continue
            if not opts:
                if last:
                    s.add(cz.BoolVal(False))
                cur.append(False)
                continue
            disj = opts[0] if len(opts) == 1 else cz.Or(opts)
            if last:
                s.add(disj)
                cur.append(True)
            else:
                b = cz.Bool(f"pay_{k}_{a}")
                s.add(cz.Implies(b, disj))
                cur.append(b)
        prev = cur

    total = cz.Sum(x)
    return s, {"x": x}, ("minimize", total)

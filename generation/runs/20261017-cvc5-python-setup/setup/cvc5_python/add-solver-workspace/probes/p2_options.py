import cvc5
tm = cvc5.Solver()
names = tm.getOptionNames()
keys = [n for n in names if any(k in n for k in ("arith", "nl-", "tlimit", "incremental", "produce-models", "timeout", "sat-random", "decision", "bv-solver", "cegqi", "quant-"))]
for n in sorted(keys):
    print(n, tm.getOptionInfo(n).currentValue if hasattr(tm.getOptionInfo(n), 'currentValue') else '')

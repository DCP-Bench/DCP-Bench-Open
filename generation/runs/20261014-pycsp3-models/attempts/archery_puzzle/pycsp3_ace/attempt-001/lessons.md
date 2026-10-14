A list comprehension of Var(...) fails: 'TypeError: The variable identifier [ is not valid' (pycsp3 takes the name from the declaration line). Use one VarArray with a shared domain and post per-element bounds as constraints.
Run pycsp3 locally with: python model.py -data=inst.json -ev -output=./out/ to see the compile traceback; evaluation.check only reports SystemExit: 1.

from pycsp3 import *

# statements[k] is 1 if statement k+1 is true, 0 if it is false
statements = VarArray(size=5, dom={0, 1})
satisfy(
    # statement 1 is true exactly when exactly one of the statements is false
    (statements[0] == 1) == (Sum(statements) == 4),
    # statement 2 is true exactly when exactly two of the statements are false
    (statements[1] == 1) == (Sum(statements) == 3),
    # statement 3 is true exactly when exactly three of the statements are false
    (statements[2] == 1) == (Sum(statements) == 2),
    # statement 4 is true exactly when exactly four of the statements are false
    (statements[3] == 1) == (Sum(statements) == 1),
    # statement 5 is true exactly when exactly five of the statements are false
    (statements[4] == 1) == (Sum(statements) == 0),
)

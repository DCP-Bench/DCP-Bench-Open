#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/five_statements.py
# Source description: From 'Puzzle: Joyner' five statements' http://strathmaths.wordpress.com/2012/10/17/puzzle-joyners-five-statements
# Misc: The following little logical teaser appears as 'Ponderable 1.1.3' in David Joyner's book Adventures in Group Theory (Johns Hopkins University Press, 2008; also available to download for free).

"""
Determine which of the following statements is true.

 - Exactly one of these statements is false.
 - Exactly two of these statements are false.
 - Exactly three of these statements are false.
 - Exactly four of these statements are false.
 - Exactly five of these statements are false.

Print whether each statement is true or false as 0/1 values (statements), with the same order as the input data.
"""

from cpmpy import *
import json

statements = boolvar(shape=5)

model = Model([statements[i] == (sum(statements == 0) == i+1) for i in range(5)])

model.solve()

solution = {"statements": statements.value().tolist()}
print(json.dumps(solution))

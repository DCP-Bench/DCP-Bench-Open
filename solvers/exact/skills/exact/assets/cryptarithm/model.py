"""Solve SEND + MORE = MONEY: a digit for each letter, all letters different.

Each letter gets a value variable and one-hot indicators for its digit. Values are
tied to indicators, the indicators of different letters are all different, and the
sum is written in place values: the addends minus the sum equals zero.
"""
from exact import Exact

ADDENDS = ["SEND", "MORE"]
TOTAL = "MONEY"
WORDS = ADDENDS + [TOTAL]
LETTERS = sorted(set("".join(WORDS)))

solver = Exact()
y = {L: [f"y_{L}_{d}" for d in range(10)] for L in LETTERS}
value = {L: f"digit_{L}" for L in LETTERS}
for L in LETTERS:
    solver.addVariable(value[L], 0, 9)
    for d in range(10):
        solver.addVariable(y[L][d], 0, 1)
    # exactly one digit per letter ...
    solver.addConstraint([(1, y[L][d]) for d in range(10)], True, 1, True, 1)
    # ... and the value variable equals that digit
    solver.addConstraint([(d, y[L][d]) for d in range(10)] + [(-1, value[L])],
                         True, 0, True, 0)

# all different: each digit is used by at most one letter
for d in range(10):
    solver.addConstraint([(1, y[L][d]) for L in LETTERS], False, 0, True, 1)

# a word of more than one letter does not start with 0
for word in set(WORDS):
    if len(word) > 1:
        solver.addConstraint([(1, y[word[0]][0])], False, 0, True, 0)

# sum of the addends minus the total, in place values; zero coefficients are dropped
coef = {L: 0 for L in LETTERS}
for word in ADDENDS:
    for pos, ch in enumerate(reversed(word)):
        coef[ch] += 10 ** pos
for pos, ch in enumerate(reversed(TOTAL)):
    coef[ch] -= 10 ** pos
terms = [(c, value[L]) for L, c in coef.items() if c != 0]
solver.addConstraint(terms, True, 0, True, 0)

status = solver.runFull(optimize=False)
print("status:", status)
if status == "SAT":
    digits = dict(zip(LETTERS, solver.getLastSolutionFor([value[L] for L in LETTERS])))
    numbers = [int("".join(str(digits[ch]) for ch in word)) for word in WORDS]
    print("letters:", " ".join(f"{L}={digits[L]}" for L in LETTERS))
    print(f"{numbers[0]} + {numbers[1]} = {numbers[2]}")
    print("all letters different:", len(set(digits.values())) == len(LETTERS))

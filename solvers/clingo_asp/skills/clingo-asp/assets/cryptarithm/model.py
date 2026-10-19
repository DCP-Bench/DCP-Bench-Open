"""Cryptarithms: each letter a distinct digit, no leading zero, one weighted sum equal to zero."""
import clingo

PUZZLES = [
    (["SEND", "MORE"], "MONEY"),   # the classic: 9567 + 1085 = 10652
    (["AB", "AB"], "AAA"),         # no solution: AAA = 111*A cannot equal 2*(10A+B)
]

PROGRAM = """
% Each letter gets exactly one digit.
1 { val(L,D) : D = 0..9 } 1 :- letter(L).

% Distinct letters get distinct digits.
:- val(L1,D), val(L2,D), L1 < L2.

% A leading letter of a multi-letter word is not zero.
:- lead(L), val(L,0).

% The weighted digit sum of addends minus total is zero. Negative weights
% subtract. Each tuple carries the letter, so equal products do not collapse.
:- #sum { W*D,L : val(L,D), weight(L,W) } != 0.

#show val/2.
"""


def facts_for(addends, total):
    """Letter weights: for each letter, sum over addends of 10^place, minus the total's."""
    weight = {}
    for word, sign in [(w, 1) for w in addends] + [(total, -1)]:
        for place, letter in enumerate(reversed(word)):
            weight[letter] = weight.get(letter, 0) + sign * 10 ** place
    lines = [f'letter("{c}").' for c in weight]
    lines += [f'weight("{c}",{w}).' for c, w in weight.items()]
    lines += [f'lead("{w[0]}").' for w in addends + [total] if len(w) > 1]
    return "\n".join(lines)


for addends, total in PUZZLES:
    ctl = clingo.Control()
    ctl.add("base", [], PROGRAM)
    ctl.add("base", [], facts_for(addends, total))
    ctl.ground([("base", [])])

    digits = None
    with ctl.solve(yield_=True) as handle:
        for model in handle:                      # models = 1 by default
            digits = {atom.arguments[0].string: atom.arguments[1].number
                      for atom in model.symbols(shown=True)}
        result = handle.get()

    name = " + ".join(addends) + " = " + total
    if result.satisfiable:
        print(name, "->", " ".join(f"{c}={d}" for c, d in sorted(digits.items())))
    else:
        print(name, "-> no solution, unsatisfiable:", result.unsatisfiable)

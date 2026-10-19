"""Enumerate every subset of the numbers 1..6 whose sum is 7."""
import clingo

ITEMS = range(1, 7)
TARGET = 7

PROGRAM = """
% Each item is either in the subset or not.
{ in(I) : item(I) }.

% Each chosen item gets one label. Without projection each labelling
% is a separate model, even though the shown answer is the same.
1 { label(I,L) : level(L) } 1 :- in(I).
level(low;high).

% The subset must sum to the target.
:- target(T), #sum { I : in(I) } != T.

#show in/1.
"""

ctl = clingo.Control()
ctl.configuration.solve.models = 0            # enumerate all models
ctl.configuration.solve.project = "show"      # one model per shown answer
ctl.add("base", [], PROGRAM)
ctl.add("base", [], "".join(f"item({i}).\n" for i in ITEMS) + f"target({TARGET}).\n")
ctl.ground([("base", [])])

answers = []
with ctl.solve(yield_=True) as handle:
    for model in handle:
        answers.append(sorted(atom.arguments[0].number for atom in model.symbols(shown=True)))
    result = handle.get()

print("Exhausted:", result.exhausted)
for subset in answers:
    print("subset:", subset)
print("Solutions:", len(answers))

"""0/1 knapsack: choose items to maximise total value within a weight limit."""
import clingo

ITEMS = {  # name: (weight, value)
    "tent": (4, 6), "stove": (3, 5), "rope": (2, 3), "lamp": (1, 2), "book": (3, 4),
}
CAPACITY = 7

PROGRAM = """
% Each item is taken or left.
{ take(I) : item(I) }.

% Total weight must not exceed the capacity.
:- capacity(C), #sum { W,I : take(I), weight(I,W) } > C.

% Maximise the total value of the taken items.
#maximize { V,I : take(I), value(I,V) }.

#show take/1.
"""

facts = [f"item({name})." for name in ITEMS]
facts += [f"weight({name},{w}). value({name},{v})." for name, (w, v) in ITEMS.items()]
facts.append(f"capacity({CAPACITY}).")

ctl = clingo.Control()
ctl.configuration.solve.opt_mode = "optN"   # improving models; the last one is a proven optimum
ctl.add("base", [], PROGRAM)
ctl.add("base", [], "\n".join(facts))
ctl.ground([("base", [])])

with ctl.solve(yield_=True) as handle:
    last = None
    for model in handle:
        if model.optimality_proven:
            last = model
    result = handle.get()

taken = sorted(str(a.arguments[0]) for a in last.symbols(shown=True))
print("Optimal:", result.exhausted and last.optimality_proven)
print("Best value:", last.cost[0] * -1)
print("Taken:", ", ".join(taken))

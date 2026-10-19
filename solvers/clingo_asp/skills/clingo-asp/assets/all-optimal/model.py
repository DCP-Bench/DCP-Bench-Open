"""Pick one site for a depot at minimum travel cost; enumerate every site that ties for the best."""
import clingo

COSTS = {"a": 5, "b": 3, "c": 3, "d": 7}

PROGRAM = """
% Exactly one site is chosen.
1 { open(S) : site(S) } 1.

% Minimise the travel cost of the chosen site.
#minimize { C,S : open(S), cost(S,C) }.

#show open/1.
"""

ctl = clingo.Control()
ctl.configuration.solve.opt_mode = "optN"     # keep improving, then enumerate optima
ctl.configuration.solve.models = 0            # ... all of them
ctl.configuration.solve.project = "show"      # one model per shown answer
ctl.add("base", [], PROGRAM)
ctl.add("base", [], "".join(f"site({s}). cost({s},{c}).\n" for s, c in COSTS.items()))
ctl.ground([("base", [])])

optimal = []
with ctl.solve(yield_=True) as handle:
    for model in handle:
        # Models before the proof are only improvements; keep proven optima.
        if model.optimality_proven:
            optimal.append((model.cost[0], sorted(str(s.arguments[0]) for s in model.symbols(shown=True))))
    result = handle.get()

print("Exhausted:", result.exhausted)
print("Optimum:", optimal[0][0])
for _, sites in sorted(optimal):
    print("optimal site:", sites[0])
print("Optimal solutions:", len(optimal))

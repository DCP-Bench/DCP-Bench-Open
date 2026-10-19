"""Single machine: order four tasks with precedences, no overlap, minimal makespan."""
import clingo

TASKS = {"prep": 3, "cut": 2, "weld": 4, "paint": 2}   # name: duration
PRECEDES = [("prep", "weld"), ("cut", "paint")]        # first must end before second starts
HORIZON = 20

PROGRAM = """
% Every task starts at one time within the horizon.
1 { start(T,S) : time(S) } 1 :- task(T).

% Two tasks cannot run at the same time on the machine.
:- start(T1,S1), start(T2,S2), T1 < T2, dur(T1,D1), dur(T2,D2),
   S1 < S2 + D2, S2 < S1 + D1.

% A task starts only after its predecessor has finished.
:- before(A,B), start(A,SA), dur(A,DA), start(B,SB), SB < SA + DA.

% Makespan: the latest finishing time. The 0 element keeps the maximum
% defined even when no task is scheduled.
end(T,E) :- start(T,S), dur(T,D), E = S + D.
makespan(M) :- M = #max { 0,none ; E,T : end(T,E) }.

#minimize { M : makespan(M) }.

#show start/2.
#show makespan/1.
"""

facts = [f"task({t}). dur({t},{d})." for t, d in TASKS.items()]
facts += [f"before({a},{b})." for a, b in PRECEDES]
facts += [f"time(0..{HORIZON})."]

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

print("Optimal:", result.exhausted and last.optimality_proven)
for atom in sorted(last.symbols(shown=True), key=str):
    if atom.name == "start":
        task, begin = atom.arguments
        print(f"{task} starts at {begin.number}")
print("Makespan:", last.cost[0])

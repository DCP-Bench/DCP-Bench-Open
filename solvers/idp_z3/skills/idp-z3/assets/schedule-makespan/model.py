"""Five jobs on one machine with precedences: minimise the makespan, under a time limit.

Theory.optimize has no time limit and cannot tell "infeasible" from "z3 gave up", so this
example drives the z3 Optimize object that IDP-Z3 builds for the theory directly.
"""
import z3
from idp_engine import IDP, Theory

duration = [3, 2, 4, 1, 2]
before = [(0, 2), (1, 2), (2, 4)]          # (a, b): job a ends before job b starts
horizon = sum(duration)

KB = """
vocabulary V {
    type Job <: Int
    type Time <: Int
    dur: Job -> Int
    prec: Job * Job -> Bool
    start: Job -> Time
    makespan: () -> Int
}
theory T: V {
    // one machine: two jobs never overlap
    ! i, j in Job: i < j => start(i) + dur(i) =< start(j) | start(j) + dur(j) =< start(i).
    // precedences
    ! i, j in Job: prec(i, j) => start(i) + dur(i) =< start(j).
    // every job ends by the makespan
    ! j in Job: start(j) + dur(j) =< makespan().
}
"""
structure = f"""
structure S: V {{
    Job := {{0..{len(duration) - 1}}}.
    Time := {{0..{horizon}}}.
    dur := {{{", ".join(f"{j}->{d}" for j, d in enumerate(duration))}}}.
    prec := {{{", ".join(f"({a},{b})" for a, b in before)}}}.
}}
"""
kb = IDP.from_str(KB + structure)
theory = Theory(*kb.get_blocks("T, S"))


def term(code):
    """The z3 expression of a ground term such as "start(2)"."""
    return theory.assignments[code].sentence.translate(theory)


optimizer = theory.optimize_solver          # a z3.Optimize holding the grounded theory
theory._add_assignment(optimizer)           # adds the structure's values (private API, as Theory.optimize does)
optimizer.set("timeout", 10_000)            # milliseconds
handle = optimizer.minimize(term("makespan()"))
status = optimizer.check()
if status == z3.unsat:
    print("status: infeasible")
elif status != z3.sat:
    print("status: unknown,", optimizer.reason_unknown())
else:
    low, high = optimizer.lower(handle), optimizer.upper(handle)
    if not (z3.is_int_value(low) and z3.is_int_value(high)):
        print(f"status: unbounded objective (between {low} and {high})")
    elif low.as_long() != high.as_long():
        print(f"status: optimum not proven (between {low} and {high})")
    else:
        model = optimizer.model()
        starts = [model.eval(term(f"start({j})"), model_completion=True).as_long()
                  for j in range(len(duration))]
        print(f"Optimal makespan: {low.as_long()}")
        print(f"Starts: {starts}")

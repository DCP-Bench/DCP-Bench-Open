# Lessons from the swipl_clpfd worker chunk (run 20261001T1218Z-swipl-ff16)

Proposals for `solvers/swipl_clpfd/skills/swipl-clpfd`. Each one is backed by an
evaluation in this run; none has been applied.

1. Existential auxiliary variables put in `Vars` make the driver enumerate every
   assignment of them before it can reach a second distinct output. A set of
   weights with several ways of weighing each target is reported once per way
   (broken_weights attempt-002, json:3: first solution checked, second never
   reached in 181 s). Prefer an encoding in which the auxiliaries are functions
   of the outputs (coin3_application attempt-002: reachable amounts computed
   denomination by denomination), or leave a purely existential variable out of
   `Vars` when its constraint is complete once the outputs are ground
   (broken_weights attempt-003: `element/3` over fixed sums, two-variable sum).
2. Failing optimisation that times out before the first solution is reported as
   `no_solution` (runner status `unsat`) at about the execution limit, not as
   `execution_timeout`. Measured: csplib_013 attempt-001 json:8, 181.9 s,
   `runner_status.status = unsat`; the same model with the objective replaced
   by a fixed host count reports `execution_timeout`. The cause (the library's
   min/max labelling catching the time limit) is inferred from the library
   source as I remember it, not verified here.
3. `ff` selects the smallest domain over all of `Vars`, so 0/1 helper variables
   in `Vars` are labelled before the decision variables. Keep helpers out of
   `Vars` when they follow from the rest (car_sequencing, battleships) and use
   `labeling_options/1` deliberately.
4. Objective-first labelling (objective variable first in `Vars`, `leftmost`)
   found the optimum much sooner than improving a first arbitrary solution
   (equal_sized_groups attempt-002: 5/5 accepted; attempt-001 found no solution
   in 186 s).
5. A nonlinear `A * B #= N * N` with a large holey domain cost about 0.5 s per
   labelled value of A (cmo_2012, measured by a stderr timing in a scratch
   model); `tuples_in([[N, P]], Squares)` over the squares of 0..max cut the
   whole instance set from one timeout plus a 155 s pass to 4 s each.
6. Boolean 0/1 flags per code with `A + B #=< 1` style neighbour rules, and
   labelling the occupied flags before the codes, took csplib_014 from two
   timeouts and 118 s on the example to 5/5 accepted (example 2.4 s).
7. In `yall`, a free variable of the lambda body that is not in `{...}` is
   renamed per call. A `foldl` lambda that used an outer `NCars` raised an
   instantiation error until `{NCars}/` was added. Lambdas that build an index
   with `#=` inside the body print a "Test is always false" compile warning;
   a named helper predicate avoids it.
8. `scalar_product/4` needs integer coefficients; a product of two variables
   (weight times side) raises an instantiation error and has to be an explicit
   `P #= W * S` term.

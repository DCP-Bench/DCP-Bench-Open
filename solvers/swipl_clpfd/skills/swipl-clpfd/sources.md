# Sources for `swipl-clpfd`

Tested with SWI-Prolog 9.2.9 (`swipl --version` in the `dcp-eval/swipl_clpfd:v1` image, x86_64 Linux, Python 3.11 in the same image), with library(clpfd) and library(time) bundled.

Refactored from the earlier integration skill for this solver; examples verified inside the dcp-eval/swipl_clpfd:v1 image.

Existing skills: none found for SWI-Prolog CLP(FD) when this skill was written.

Documentation this skill's instructions were written from. Add an entry whenever a claim here comes from a specific page or version.

- <https://www.swi-prolog.org/pldoc/man?section=clpfd> — library(clpfd) reference, accessed 2026-09-14
- <https://www.swi-prolog.org/pldoc/doc_for?object=labeling/2> — labeling/2 and its option categories, accessed 2026-09-14
- <https://www.swi-prolog.org/pldoc/man?section=time> — library(time): `call_with_time_limit/2` and `time_limit_exceeded`, checked 2026-10-15
- <https://github.com/SWI-Prolog/swipl-devel/blob/master/library/clp/clpfd.pl> — the clpfd source; its header comments hold the SEND+MORE, Sudoku and eight-queens examples, checked 2026-10-15
- <https://www.swi-prolog.org/build/Debian.md> — install routes: PPA for current releases, distribution packages may lag, checked 2026-10-15
- <https://hub.docker.com/_/swipl> — `swipl:9.2.9`, the image the tested runtime was built from

Every constraint in the API tables and every idiom in this skill was checked by running SWI-Prolog 9.2.9 inside the dcp-eval/swipl_clpfd:v1 image, not taken from documentation alone:

- `all_distinct/1`, `all_different/1`, `sum/3`, `scalar_product/4`,
  `element/3`, `global_cardinality/2`, `circuit/1`, `tuples_in/2`,
  `lex_chain/1`, `chain/2`, `serialized/2`, `disjoint2/1`,
  `cumulative/2` with `task/5` and `limit/1`, `automaton/3`, `transpose/2`,
  `#==>`, `#\/` and `fd_dom/2` all resolve and propagate as described.
- `element/3` is 1-based and accepts a variable index, which is what makes the
  flatten-and-index idiom the way to read a matrix cell chosen by a decision
  variable. `nth1/3` with an unbound index enumerates positions instead of
  posting a constraint.
- There is no `nvalue/2` and no `count/4` in SWI-Prolog's clpfd; counting goes
  through `#<==>` reification plus `sum/3`, or `global_cardinality/2` with a
  variable count, both of which were run.
- Labelling options: one option per category is enforced, and two from one
  category raise `domain_error(consistent_labeling_options, _)`; `random_value/1`
  and `random_variable/1` take a seed.
- `labeling([min(Expr)], Vars)` returns the optimum first. When `Vars` is labelled, `Expr` must be
  ground: a variable fixed by the constraints from `Vars` is enough (`S #= 3 - R`, label `[R]`, works), but a
  free variable such as `Q` in `max(P+Q)` with only `[P]` labelled raises `instantiation_error`.
- `Y ins 0..3` on one variable raises `instantiation_error` (`ins` takes a list); `X in 0..N-1` with `N` bound
  raises `domain_error(clpfd_domain, 0..N-1)`.
- Bounded descent (the anytime pattern in SKILL.md): post `Total #=< Bound`, label, record, tighten; ran on a
  three-item knapsack (max, optimum 12) and on the jobshop ft06 instance (min, 55 within 15 s, probed in the image).
- Command line: `swipl model.pl inst.json` gives `main/1` the argument `inst.json`; `json_read_dict/2`,
  `get_dict/3` and `json_write_dict/3` with `width(0)` behave as shown in SKILL.md.
- Labelling an unbounded variable raises
  `Arguments are not sufficiently instantiated`, which is why the skill insists
  on `ins`/`in` before labelling.
- `maplist/5` is the widest `maplist` in SWI-Prolog 9.2.9: a goal with six or more
  arguments is an unknown procedure.
- A lambda `[X]>>Goal` does not see an outer variable unless it is listed in
  `{...}`; the unlisted variable was a fresh variable inside the lambda.
- Uncaught errors under `initialization(main, main)` exit with status 2, a failing
  `main` with status 1, and a syntax error skips only its clause.

## Independent toy test (add-solver)

An independent tester solved the add-solver toy problems from this skill alone, in the
dcp-eval/swipl_clpfd:v1 image (read-only mount, `--network none`), with the runner's timeout raised to
400 s for the final run. Result: **18/18 passed** with the final models, with one caveat: jobshop/ft06
needs about 300 s with the plain `labeling([min(Mk)], ...)` and fails at the runner's default 120 s
timeout; it passes at 400 s and, with the bounded descent in SKILL.md, reaches 55 within 15 s.

| problem / instance | first run | repairs | final |
|---|---|---|---|
| n-queens / n3, n4, n8 | FAIL (`0..N-1` domain bug) | 1 | PASS |
| n-queens-all / n6, n8 | FAIL (same bug) | 1 | PASS |
| knapsack / small, p01 | PASS | 0 | PASS |
| knapsack-all-optimal / ties, unique, fourteen | PASS | 0 | PASS |
| graph-colouring / cycle6, k4-tail, petersen | FAIL (`Max ins` for a scalar; `0..N-1`) | 2 | PASS |
| cryptarithm / send-more-money, two-two-four, ab-ab-aaa | PASS | 0 | PASS |
| jobshop / small | PASS | 0 | PASS |
| jobshop / ft06 | TIMEOUT at 300 s | 2 | PASS at 400 s only; FAIL at 120 s |

Passed: 18/18 at the final run (ft06 needs the longer timeout). The fixes from this round address the
tester's findings: JSON and argv guidance, the optimisation rule, the bounded descent for proof-heavy
optimisation, the `0..N-1`, `Max ins` and `ins` on one variable mistakes, the serialized/cumulative choice,
and reporting an unfinished run.

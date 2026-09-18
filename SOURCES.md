# DCP-Bench-Open Sources

The dataset contains problems gathered from different sources.

- `aplai_course`: Problems from the APLAI course of KU Leuven, 2023-2024. As modelled here: https://github.com/kostis-init/LLM-CP-Modeling/tree/main/data/APLAI_course
  - All 18 problems are added.
- `complex_or`: Problems from the ComplexOR repository, found here: https://github.com/xzymustbexzy/Chain-of-Experts
  - Those already modelled in other folders (e.g. knapsack) and those with heavy float parameters/objective values are excluded.
- `cpmpy_examples`: Problems from the cpmpy examples folder, https://github.com/CPMpy/cpmpy/tree/master/examples
  - All included, except for the ones that require enumeration of all solutions (e.g. `solveAll`).
- `csplib`: Problems from the csplib, https://www.csplib.org/Problems/
  - For now, only the ones modelled in the cpmpy repository are included (https://github.com/CPMpy/cpmpy/tree/master/examples/csplib), and the ones modelled by Hakan Kjellerstrand (http://www.hakank.org/cpmpy/).
- `hakan_examples`: Models created by Hakan Kjellerstrand, http://www.hakank.org/cpmpy/
  - In progress with alphabetical order. Currently, includes all problems until `knights_tour_circuit.py`, excluding the following:
    - Those already modelled in other folders (e.g. aplai_course, cpmpy_examples, csplib)
    - Those that contain `solveAll` (counting solutions).
    - Global constraints tests, e.g. http://www.hakank.org/cpmpy/atmost_test.py

## Generated models

`generated_models/<problem>/<framework>/<submission>/` holds models produced by
generative systems, not ground truth. Every one was generated in this repository
by the `model-generator` skill against an integration under `solvers/`, and kept
only because the evaluator accepted it.

Each model directory holds the model and one `record.json`. Its `verdict_source`
is `container_evaluator`, and the evaluator's full result is embedded in the
record. `generation/runs/` holds how each model was made.

Two other corpora used to live here: one imported from the CP-Bench leaderboard,
and a set of abbots-puzzle demo models written across frameworks that have no
integration here. Neither was judged by the evaluator in this repository, so
neither counted as coverage, and both have been removed.

## Dataset decisions

Some changes made to the source problems (many more may have been made), and the reasoning behind them.

**Removed as provably unsatisfiable.** QG3 quasigroup orders m in
{2,3,5,6,7,10,11,14,15,18,19}, and perfect-square-placement `problem3`. For the
QG3 identity `(a*b)*(b*a)=a`, a necessary condition is m congruent to 0 or 1
modulo 4; order 5 is also impossible. See
[Fujita, Slaney and Bennett, IJCAI 1993, page 55](https://www.ijcai.org/Proceedings/93-1/Papers/008.pdf).
A reference with no solution cannot judge a candidate. A deterministic test
checks this necessary condition on the retained orders; it does not establish
that every retained instance is satisfiable.

**Translated.** The nonogram reference was moved from an OR-Tools native
automaton to CPMpy's `Regular` constraint. Equivalence was established by
solving all 14 listed instances and re-checking each board against the
row/column block rules — by testing, not by proof.

**Retained as they appear in the source.** Named duplicates of an embedded
example (nonogram `bear`, template-design `catfood2`, perfect-square-placement
`problem2`). The evaluator deduplicates by declared data fields and ignores
metadata: the embedded example takes precedence, otherwise the first JSON
record is kept with its metadata and original `json:<index>` ID.


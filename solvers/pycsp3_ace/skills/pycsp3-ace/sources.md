# Sources for `pycsp3-ace`

Tested with pycsp3 2.6.1 (MIT) and its bundled ACE 2.6 (`ACE-2.6.jar`), lxml 6.1.3,
Python 3.12.11, OpenJDK 17.0.20, Debian 12 (in a container, no network).

Existing skills: none found for PyCSP3 or ACE (not searched on skills.sh).

- <https://pypi.org/project/pycsp3/2.6.1/>: pycsp3 2.6.1 wheel (sha256 06e86b0b8aaed3a2f72acf9d5cca32f0b7ef86a45fa0d30a2308871883dbf4d5), read from the extracted package: `__init__.py` (data binding, `solve`, `minimize`, `status`, `bound`, `n_solutions`, `solver`, `clear`), `compiler.py` (`-data`, `-output`, one-key data, named-tuple conversion), `functions.py` (`value`, `values`), `solvers/solver.py` (result extraction, solver log, the `d FOUND SOLUTIONS` parsing), `pycsp3/solvers/ace/ace.py`
- <https://pycsp.org/>: PyCSP3 documentation, for the modelling API (`Var`, `VarArray`, `satisfy`, `minimize`, global constraints); installation page <http://pycsp.org/documentation/installation>; models <http://pycsp.org/models/>
- <https://github.com/xcsp3team/pycsp3>: source; `docs/optionsSolvers.pdf` for solver options (named in `solve()`'s docstring)
- <https://www.cril.univ-artois.fr/~lecoutre/ace/>: ACE solver, bundled as ACE-2.6.jar in pycsp3 2.6.1; its option list from `java -jar ACE-2.6.jar` (`-t`, `-s`, `-seed`, `-v`, `-ev`)
- <https://github.com/xcsp3team/ace>: ACE source
- The XCSP3 `SolutionChecker` class in `ACE-2.6.jar` (`org.xcsp.parser.callbacks`); each XCSP keyword in `org/xcsp/common/Constants.class` (`KEYWORDS`)

Verified by running (pycsp3 2.6.1, ACE 2.6, OpenJDK 17):

- Each construct in `references/language.md` and each code block in `SKILL.md` and
  `references/examples.md`, with a solve and a print appended where the block has none.
  The failures listed as "Dropped" in `language.md` were reproduced with the messages shown.
- Each reserved identifier, the 32-bit value limit and the domain-size limit in
  `references/language.md`, probed one by one (domain-size limit with a 1200 MiB Java heap).
- `solve()` statuses: `OPTIMUM` (proven), `SAT` for an optimisation stopped by `-t=2s`
  (12-mark Golomb ruler, bound 100), `UNKNOWN` for a satisfaction stopped before any
  solution and for an ACE error, `UNSAT` with `n_solutions()` `None`.
- ACE errors land in the `solver_*.log` file (`Fatal Error: The id E is a keyword`,
  `Fatal Error: Too big integer value 2147483640`, `! ERROR (use -ev for more details)`);
  `java -jar ACE-2.6.jar model.xml -ev` prints `java.lang.OutOfMemoryError: Java heap space`.
- `n_solutions()` returned 500 for 1500 stored solutions and 197 for 44,197; the log's
  `d COMPLETE EXPLORATION` / `d INCOMPLETE EXPLORATION` lines; `solver().last_log`.
- An unconstrained array element reads `*`; `value()` of an unconstrained `Var` raises
  `AssertionError`.
- `Product` of four variables: ACE reported `[100, 50, 1, 1]` for `Product == 5040`; the
  `SolutionChecker` printed `INVALID Solution!`. The split into binary products gives valid
  solutions.
- `-data=` with a `_`-prefixed key raises `ValueError: Field names cannot start with an
  underscore`; a one-key file binds `data` to the bare value; plain `json` with
  `sys.argv[1]` works next to `from pycsp3 import *`.
- `clear()` followed by a rebuild (function returning a `VarArray` with `id=`) solves a
  second model in the same script.
- A small model takes about 2 s wall in total (measured twice: 2.02 s, 2.16 s).
- Every example in `assets/` with `check_assets.py` (9/9 passed).
- `minimize(NValues(c))` as the objective: proven optima of 2 (6-cycle), 4 (K4), 3 (Petersen)
  and 4 (wheel, `assets/colouring-min-colours`).
- `solve(sols=ALL)` on an infeasible model: `UNSAT`, empty `values`, `n_solutions()` `None`.
- Compiled XML and `solver_*.log` go to the current working directory; a read-only one raises
  `OSError: [Errno 30] Read-only file system` from `solve()`.
- The job-shop asset with six machines reaches `OPTIMUM` with machines taken from the data.

Modelling lessons (Boolean indicators instead of `NValues`, transpose symmetry with
`LexIncreasing`, `Regular` per nonogram line, splitting `Product`) come from campaigns of
hundreds of generated PyCSP3 models; the `NValues` timing is not re-measured here.

Independent toy test: 18/18

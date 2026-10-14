# Sources for `pycsp3-ace`

Documentation this skill's instructions were written from. Add an entry
whenever a claim here comes from a specific page or version.

- <https://pypi.org/project/pycsp3/2.6.1/> — pycsp3 2.6.1 wheel (sha256 06e86b0b8aaed3a2f72acf9d5cca32f0b7ef86a45fa0d30a2308871883dbf4d5), read from the extracted package: `__init__.py` (data binding, `solve`, `minimize`), `compiler.py` (`-data`, `-output`, one-key data), `solvers/solver.py` (result extraction, solver log), `solvers/ace/ace.py`
- <https://pycsp.org/> — PyCSP3 documentation, for the modelling API (`Var`, `VarArray`, `satisfy`, `minimize`, global constraints)
- <https://www.cril.univ-artois.fr/~lecoutre/ace/> — ACE solver, bundled as ACE-2.6.jar in pycsp3 2.6.1

Verified in the `pycsp3_ace` image (pycsp3 2.6.1, ACE-2.6, OpenJDK 17):

- `data.field` and `data["_field"]` access; a one-key instance and an instance
  with metadata strings both run.
- 2-D `VarArray(size=[2, 3], ...)` gives nested lists; `AllDifferent`, `Sum`,
  `Or` and element-wise comparisons solve.
- An output that no constraint mentions raises the explicit error described in
  the skill.
- A minimisation and a maximisation return the optimum and its solutions; an
  auxiliary variable that repeats output assignments is handled by the rounds.

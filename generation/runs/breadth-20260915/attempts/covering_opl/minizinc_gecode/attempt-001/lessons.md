`Qualified` is a ragged array: one list of qualified workers per task, of
differing lengths. MiniZinc's data interface has no representation for that — a
list of lists binds as a rectangular 2D array — so the runner fails with
"non-uniform array literal" before the model is even solved. A model cannot work
around it: the shape of the instance field is the obstacle, and reshaping it
inside run.py would be the "problem-specific encoding" the integration's skill
says needs a separate converter rather than quiet reinterpretation.
Recorded as a blocker for this pair.

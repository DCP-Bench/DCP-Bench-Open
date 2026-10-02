# Lessons (minizinc_gecode, csplib_001_car_sequencing)

Without search annotations, Gecode's default search is sensitive to how the model is stated,
and to which helper arrays are declared. Measured with a 60 s limit, one solution, same constraints:
- attempt-001 form (element + declared prefix-count arrays): no solution on json:1, 2, 3.
- bits as "car does not need option" + table(type, bits) + implied prefix counts written as
  direct sums (no declared helper array): solved 13 of the 21 large instances (json:1, 3-6, 8-12, 15, 17, 21).
- same with the prefix counts as a declared `array of var int`: json:2, 3 solved, json:1, 4, 5 not.
- bits as "car needs option": none of json:1, 2, 3, 7, 13, 14.
- implied prefix counts removed: none of json:1, 2, 7, 13, 14, 16.
- option columns ordered most-loaded first (attempt-003): 14 of 21; least-loaded first solved json:14, 16, 19
  that the other order did not. The full evaluation of attempt-003 accepted 16 of 22 instances.
Evidence: attempt-001/002/003 evaluation.json in this directory tree.

attempt-002 uses `solve :: int_search(sequence, input_order, indomain_max) satisfy;` and was accepted
on 4 of 22 instances; it is not retained, because the skill says search annotations are not available.
The evaluator itself accepts an annotated solve item for a satisfaction problem.

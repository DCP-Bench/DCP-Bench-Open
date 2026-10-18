# handshaking, eclipse_clp, attempt-003 (evaluated, not retained)

Result: accepted = true overall, but instances_checked 3 of 5 (0.6 < 0.8). Not retained.
Timeouts: `example` (num_couples 8) and `json:4` (num_couples 6), both
"driver outlived the execution budget". Checked and accepted: json:1 (4 couples, hil 4),
json:2 (1 couple, hil 1), json:3 (3 couples, hil 3).

Model: gfd, P = 2(n+1) persons, 0/1 matrix with H[I,J] = H[J,I], zero diagonal and zero
spouse cells, row sums as hand counts, alldifferent over Hilary and the persons other than
Jocelyn. Search: hand counts first (first_fail, indomain_max), then cells.

Measured (ad hoc runs in the image, not evaluations):
- hand counts first with indomain_min or indomain_max, or input order: n=4 about 1-3 s,
  n=5 21-25 s, n=6 over 170 s;
- cells first (indomain_max): n=5 over 170 s;
- hand counts only (n=6): over 170 s, so the time goes into refuting count vectors, not
  into the cells;
- value-first assignment (the person with count 2n, then 2n-1, ...) with cells after: n=5
  25 s, n=6 over 170 s;
- a model with `ic` and the default labelling: n=8 no solution in 180 s.

Trap hit: `Hand :: 0..P-2` inside a `for` loop reads `P` as a singleton unless `P` is in
`param(...)`. The warning comes with `instantiation fault in -(_, 0, _)`. Put every outer
variable used in the body, including bounds in `1..P`, in `param`.

Open question: the count vectors are hard to refute without the Halmos-style argument (the
person with 2n hands is adjacent to all but the spouse, so the spouse has 0). The next
attempt needs stronger propagation (an implied constraint that follows from the description,
or a different encoding) to reach n=6 and n=8 within 180 s.

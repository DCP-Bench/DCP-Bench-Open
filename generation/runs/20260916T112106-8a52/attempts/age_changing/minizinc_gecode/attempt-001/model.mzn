% Age changing: the same four operations, applied in two different orders, turn
% each spouse age into the other. The operations are +2, /8, -3 and *7,
% numbered in that order; the division is stated as a multiplication so that
% only exact eighths count, as the reference does.
include "globals.mzn";

var 16..120: m;
var 16..120: h;
array[1..4] of var 0..3: perm1;
array[1..4] of var 0..3: perm2;
array[1..5] of var 1..1000: mlist;
array[1..5] of var 1..1000: hlist;

constraint all_different(perm1);
constraint all_different(perm2);
% The same operations, but in a different order.
constraint sum(i in 1..4) (bool2int(perm1[i] != perm2[i])) > 0;

constraint hlist[1] = m;
constraint h = hlist[5];
constraint mlist[1] = h;
constraint m = mlist[5];

predicate step(var int: op, var int: old, var int: new) =
    (op = 0 -> new = old + 2)
    /\ (op = 1 -> 8 * new = old)
    /\ (op = 2 -> new = old - 3)
    /\ (op = 3 -> new = old * 7);

constraint forall(i in 1..4) (step(perm1[i], hlist[i], hlist[i + 1]));
constraint forall(i in 1..4) (step(perm2[i], mlist[i], mlist[i + 1]));

solve satisfy;

output ["{\"m\": ", show(m), ", \"h\": ", show(h), "}"];

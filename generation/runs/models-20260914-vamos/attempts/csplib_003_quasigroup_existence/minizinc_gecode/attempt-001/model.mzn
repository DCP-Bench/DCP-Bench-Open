include "globals.mzn";

int: m;

array[0..m-1, 0..m-1] of var 0..m-1: quasigroup;

constraint forall(i in 0..m-1) (
    all_different([quasigroup[i, j] | j in 0..m-1])
  /\ all_different([quasigroup[j, i] | j in 0..m-1])
);
% QG3.m: (a * b) * (b * a) = a.
constraint forall(a, b in 0..m-1) (
    quasigroup[quasigroup[a, b], quasigroup[b, a]] = a
);

solve satisfy;

output ["{\"quasigroup\": [",
        join(", ", ["[" ++ join(", ", [show(quasigroup[i, j]) | j in 0..m-1]) ++ "]" | i in 0..m-1]),
        "]}"];

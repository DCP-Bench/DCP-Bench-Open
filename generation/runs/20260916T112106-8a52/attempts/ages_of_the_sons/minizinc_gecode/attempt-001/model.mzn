% Ages of the sons: the product is 36, the sum is ambiguous, and there is a
% unique oldest. The second triple B is another factorisation of 36 with the
% same sum and a different eldest, which is what made the sum ambiguous.
var 0..36: A1; var 0..36: A2; var 0..36: A3;
var 0..36: B1; var 0..36: B2; var 0..36: B3;
var 0..1000: AS; var 0..1000: BS;

constraint A1 > A2 /\ A2 >= A3;
constraint 36 = A1 * A2 * A3;
constraint B1 >= B2 /\ B2 >= B3;
constraint A1 != B1;
constraint 36 = B1 * B2 * B3;
constraint AS = A1 + A2 + A3;
constraint BS = B1 + B2 + B3;
constraint AS = BS;

solve satisfy;

output ["{\"A1\": ", show(A1), ", \"A2\": ", show(A2),
        ", \"A3\": ", show(A3), "}"];

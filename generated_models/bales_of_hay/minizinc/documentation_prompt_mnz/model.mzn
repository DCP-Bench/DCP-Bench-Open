include "globals.mzn";

% Number of bales
int: n = 5;

% Given pairwise sums sorted
array[1..10] of int: given_sums = [80, 82, 83, 84, 85, 86, 87, 88, 90, 91];

% Decision variables: weights of each bale
array[1..n] of var 1..100: bales;

% Constraint: bales are sorted to avoid symmetric solutions
constraint forall(i in 1..n-1) (bales[i] <= bales[i+1]);

% Compute all pairwise sums
array[1..10] of var int: pair_sums = [
    bales[1] + bales[2],
    bales[1] + bales[3],
    bales[1] + bales[4],
    bales[1] + bales[5],
    bales[2] + bales[3],
    bales[2] + bales[4],
    bales[2] + bales[5],
    bales[3] + bales[4],
    bales[3] + bales[5],
    bales[4] + bales[5]
];

% The pair sums sorted must be equal to the given sums
constraint
    forall(i in 1..10) (
        pair_sums[i] in 1..100
    ) /\
    % Sort pair_sums and enforce equality with given_sums
    let {
        array[1..10] of var int: sorted_sums
    } in (
        % sorted_sums is sorted version of pair_sums
        sorted_sums = sort(pair_sums) /\
        forall(i in 1..10) (
            sorted_sums[i] = given_sums[i]
        )
    );

solve satisfy;

output [
    "{",
    "\"bales\": ", show(bales),
    "}"
];
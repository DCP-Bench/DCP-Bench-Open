% The boy passes through 5 gates, bribing each guard with half of his apples plus one.
% He must give an integer number of apples at each gate.
% After the last gate, he has no apples left.
% We want to find the number of apples before each gate and after the last gate (6 numbers in total).

include "globals.mzn";

int: num_gates = 5;

% apples[i] = number of apples before gate i (for i in 1..5)
% apples[6] = number of apples after the last gate
array[1..num_gates+1] of var int: apples;

% Constraints:
% 1) The number of apples before each gate must be positive (at least 1)
constraint forall(i in 1..num_gates) (
    apples[i] >= 1
);

% 2) After the last gate, no apples remain
constraint apples[num_gates+1] == 0;

% 3) At each gate i, the boy gives half of his apples plus one to the guard.
%    The number of apples given must be an integer.
%    So apples[i] - apples[i+1] = apples[i]/2 + 1
%    Rearranged: apples[i+1] = apples[i] - (apples[i]/2 + 1)
%    Since apples[i]/2 must be integer, apples[i] must be even.
constraint forall(i in 1..num_gates) (
    apples[i] mod 2 == 0 /\
    apples[i+1] == apples[i] - (apples[i] div 2 + 1)
);

solve satisfy;

output [
    "{",
    join(",", [show(apples[i]) | i in 1..num_gates+1]),
    "}"
];
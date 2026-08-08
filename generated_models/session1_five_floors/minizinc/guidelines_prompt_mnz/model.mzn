
include "globals.mzn";

% Decision variables: floors for Baker(B), Cooper(C), Fletcher(F), Miller(M), Smith(S)
var 1..5: B;
var 1..5: C;
var 1..5: F;
var 1..5: M;
var 1..5: S;

% All live on different floors
constraint alldifferent([B, C, F, M, S]);

% Given constraints:
constraint B != 5;           % Baker does not live on the 5th floor
constraint C != 1;           % Cooper does not live on the 1st floor
constraint F != 5 /\ F != 1; % Fletcher does not live on the 1st or 5th floor
constraint M > C;            % Miller lives on a higher floor than Cooper
constraint abs(S - F) != 1;  % Smith not adjacent to Fletcher
constraint abs(F - C) != 1;  % Fletcher not adjacent to Cooper

solve satisfy;

output [
    "{",
    join(",", [
        "\"B\": " ++ show(B),
        "\"C\": " ++ show(C),
        "\"F\": " ++ show(F),
        "\"M\": " ++ show(M),
        "\"S\": " ++ show(S)
    ]),
    "}"
];

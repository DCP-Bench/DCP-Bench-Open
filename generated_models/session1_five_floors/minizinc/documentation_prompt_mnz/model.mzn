% Include necessary library for global constraints
include "globals.mzn";

% Define the floors range
set of int: Floors = 1..5;

% Decision variables: floors where each person lives
var Floors: B; % Baker
var Floors: C; % Cooper
var Floors: F; % Fletcher
var Floors: M; % Miller
var Floors: S; % Smith

% Constraints
constraint B != 5; % Baker does not live on the fifth floor
constraint C != 1; % Cooper does not live on the first floor
constraint F != 1 /\ F != 5; % Fletcher does not live on first or fifth floor
constraint M > C; % Miller lives on a higher floor than Cooper
constraint abs(S - F) > 1; % Smith does not live adjacent to Fletcher
constraint abs(F - C) > 1; % Fletcher does not live adjacent to Cooper
constraint alldifferent([B, C, F, M, S]); % All live on different floors

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
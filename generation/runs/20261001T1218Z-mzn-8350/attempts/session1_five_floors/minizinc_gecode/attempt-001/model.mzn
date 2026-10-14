% Five floors: Baker, Cooper, Fletcher, Miller and Smith live on the first five
% floors of an apartment house, one person per floor. Clues about who cannot be
% on which floor, or next to whom, place them.
include "globals.mzn";

% the floor (1..5) each person lives on
var 1..5: B;   % Baker
var 1..5: C;   % Cooper
var 1..5: F;   % Fletcher
var 1..5: M;   % Miller
var 1..5: S;   % Smith

% Baker does not live on the fifth floor
constraint B != 5;

% Cooper does not live on the first floor
constraint C != 1;

% Fletcher does not live on either the fifth or the first floor
constraint F != 5 /\ F != 1;

% Miller lives on a higher floor than does Cooper
constraint M > C;

% Smith does not live on a floor adjacent to Fletcher's
constraint abs(S - F) != 1;

% Fletcher does not live on a floor adjacent to Cooper's
constraint abs(F - C) != 1;

% they all live on different floors
constraint all_different([B, C, F, M, S]);

solve satisfy;

output ["{\"B\": ", show(B), ", \"C\": ", show(C), ", \"F\": ", show(F), ", \"M\": ", show(M), ", \"S\": ", show(S), "}"];

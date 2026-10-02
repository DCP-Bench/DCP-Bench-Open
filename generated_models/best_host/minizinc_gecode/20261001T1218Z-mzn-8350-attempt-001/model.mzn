% Best host: six guests sit at a round table; each guest will only sit next to
% two particular other guests. Seat them in an order where every guest has
% only such neighbours (no conflicts). The guests are numbered 0 Andrew,
% 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank. This problem has no instance data:
% the guests and their likes are part of the problem statement.
include "globals.mzn";

int: n = 6;  % number of guests (and seats)
int: Andrew = 0; int: Betty = 1; int: Cara = 2; int: Dave = 3; int: Erica = 4; int: Frank = 5;

% prefs[g, 1..2] = the two guests that guest g will sit next to (fixed by the problem statement)
array[0..n - 1, 1..2] of int: prefs = array2d(0..n - 1, 1..2, [
    Dave, Frank,    % Andrew
    Cara, Erica,    % Betty
    Betty, Frank,   % Cara
    Andrew, Erica,  % Dave
    Betty, Dave,    % Erica
    Andrew, Cara    % Frank
]);

% x[i] = the guest in seat i, going around the table
array[0..n - 1] of var 0..n - 1: x;

% every guest has one seat
constraint all_different(x);

% the guest in each seat has a neighbour on each side (seat i-1 and i+1, going
% round the table) that he or she is willing to sit next to
constraint forall(i in 0..n - 1)
    (exists(j in 1..2) (prefs[x[i], j] = x[(i - 1 + n) mod n]) /\
     exists(j in 1..2) (prefs[x[i], j] = x[(i + 1) mod n]));

solve satisfy;

output ["{\"x\": [", join(", ", [show(x[i]) | i in 0..n - 1]), "]}"];

% Frog circle: arrange cards 1..n around a circle so the frog, jumping from
% each card by the number written on it, lands on every card.
include "globals.mzn";

int: n;

array[1..n] of var 1..n: x;
% Positions are 0-based in the reference; they are shifted by one here so they
% can index the card array directly.
array[1..n] of var 1..n: pos;
array[1..n] of var 1..n: visited;

constraint all_different(x);
constraint all_different(pos);
constraint all_different(visited);

% The frog starts on card 1, at the first position.
constraint x[1] = 1;
constraint pos[1] = 1;
constraint visited[1] = 1;

constraint forall(i in 2..n) (
    pos[i] = (pos[i - 1] - 1 + x[pos[i - 1]]) mod n + 1
    /\ visited[i] = x[pos[i]]
);

solve satisfy;

output ["{\"x\": [", join(", ", [show(x[i]) | i in 1..n]), "]}"];

% Broken weights: a measuring weight of total m pounds broke into n pieces of
% whole-pound weight. Find piece weights such that every whole weight from 1 to
% m can be weighed on a balance scale, where pieces may go on either pan.
include "globals.mzn";

int: m;  % total weight of the original weight
int: n;  % number of pieces

% weights[j] = weight of piece j
array[1..n] of var 1..m: weights;

% the pieces together weigh the original weight
constraint sum(weights) = m;

% Every way of using the pieces: each piece is put on the object's pan (-1),
% left off (0) or put on the other pan (1). A placement is numbered by reading
% its n choices as the digits of a base-3 number, so there are 3^n of them.
% balance[p] = (weight on the other pan) - (weight on the object's pan) for
% placement p, i.e. the object weight that this placement weighs.
% Choosing a placement for each object weight with its own variables would
% leave many equivalent choices for the same piece weights, and only the piece
% weights are the answer; listing the placements once keeps the search to the weights.
int: placements = pow(3, n);
array[0..placements - 1] of var -m..m: balance;
constraint forall(p in 0..placements - 1)
    (balance[p] = sum(j in 1..n) (((p div pow(3, j - 1)) mod 3 - 1) * weights[j]));

% every weight from 1 to m can be weighed: some placement balances it
constraint forall(i in 1..m) (exists(p in 0..placements - 1) (balance[p] = i));

solve satisfy;

output ["{\"weights\": [", join(", ", [show(weights[j]) | j in 1..n]), "]}"];

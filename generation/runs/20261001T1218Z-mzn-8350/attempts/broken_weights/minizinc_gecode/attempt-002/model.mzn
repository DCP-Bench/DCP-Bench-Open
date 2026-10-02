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

% An object of i pounds can be weighed when each piece can be put on the
% object's pan, on the other pan, or left off, so that the two pans balance.
% Instead of choosing a placement for every piece and every i (which leaves
% many placements for the same weights, and the placements are not part of the
% answer), reach[j, v] records whether a difference of v pounds between the two
% pans can be made with the first j pieces. By symmetry only differences
% v >= 0 are tracked; all differences are at most m, the total weight.
array[0..n, 0..m] of var bool: reach;

% with no pieces the pans differ by 0 pounds only
constraint forall(v in 0..m) (reach[0, v] <-> v = 0);

% piece j is left off (difference v stays), or added to the lighter side
% (the difference was |v - w| before), or added to the heavier side (the
% difference was v + w before, if that is not more than m)
constraint forall(j in 1..n, v in 0..m)
    (reach[j, v] <-> (reach[j - 1, v] \/
                      reach[j - 1, abs(v - weights[j])] \/
                      (v + weights[j] <= m /\ reach[j - 1, min(v + weights[j], m)])));

% every weight from 1 to m can be weighed with all n pieces
constraint forall(i in 1..m) (reach[n, i]);

solve satisfy;

output ["{\"weights\": [", join(", ", [show(weights[j]) | j in 1..n]), "]}"];

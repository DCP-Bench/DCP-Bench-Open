% Broken weights: a measuring weight of total m pounds broke into n pieces of
% whole-pound weight. Find piece weights such that every whole weight from 1 to
% m can be weighed on a balance scale, where pieces may go on either pan.
include "globals.mzn";

int: m;  % total weight of the original weight
int: n;  % number of pieces

% weights[j] = weight of piece j
array[1..n] of var 1..m: weights;

% x[i, j] says where piece j goes when weighing the object of i pounds:
% -1 = on the pan of the object, 0 = not used, 1 = on the other pan
array[1..m, 1..n] of var -1..1: x;

% the pieces together weigh the original weight
constraint sum(weights) = m;

% every weight i from 1 to m can be weighed: the pieces on the other pan minus
% the pieces on the object's pan balance an object of i pounds
constraint forall(i in 1..m) (sum(j in 1..n) (weights[j] * x[i, j]) = i);

solve satisfy;

output ["{\"weights\": [", join(", ", [show(weights[j]) | j in 1..n]), "]}"];

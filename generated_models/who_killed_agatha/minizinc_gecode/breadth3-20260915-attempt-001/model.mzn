include "globals.mzn";

array[int] of string: names;

% The reference numbers the residents 0 Agatha, 1 the butler, 2 Charles.
int: n = length(names);
set of int: People = 0..n-1;
int: agatha = 0;
int: butler = 1;
int: charles = 2;
int: victim = 0;

var People: killer;
array[People, People] of var bool: hates;
array[People, People] of var bool: richer;

% A killer always hates, and is no richer than, his victim.
constraint hates[killer, victim];
constraint not richer[killer, victim];
constraint forall(i in People) (not richer[i, i]);
constraint forall(i, j in People where i < j) (richer[i, j] = not richer[j, i]);
% Charles hates nobody that Agatha hates.
constraint forall(i in People) (hates[agatha, i] -> not hates[charles, i]);
% Agatha hates everybody except the butler.
constraint hates[agatha, agatha];
constraint hates[agatha, charles];
constraint not hates[agatha, butler];
% The butler hates everyone not richer than Agatha, and everyone Agatha hates.
constraint forall(i in People) (not richer[i, agatha] -> hates[butler, i]);
constraint forall(i in People) (hates[agatha, i] -> hates[butler, i]);
% Nobody hates everyone.
constraint forall(i in People) (sum(j in People) (bool2int(hates[i, j])) <= 2);

solve satisfy;

output ["{\"killer\": ", show(killer), "}"];

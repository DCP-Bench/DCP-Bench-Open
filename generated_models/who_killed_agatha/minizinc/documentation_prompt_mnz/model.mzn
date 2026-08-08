% Dreadsbury Mansion murder mystery

% Names and indices
int: Agatha = 1;
int: Butler = 2;
int: Charles = 3;
set of int: Persons = 1..3;

% Decision variables
% killer: index of the killer
var Persons: killer;

% hates[i,j] = true if person i hates person j
array[Persons, Persons] of var bool: hates;

% richer[i,j] = true if person i is richer than person j
array[Persons, Persons] of var bool: richer;

% Constraints:

% 1) The killer always hates the victim (Agatha)
constraint hates[killer, Agatha];

% 2) The killer is no richer than the victim (Agatha)
constraint not richer[killer, Agatha];

% 3) Charles hates no one that Agatha hates
% For all j: if Agatha hates j then Charles does not hate j
constraint forall(j in Persons) (
    hates[Agatha, j] -> not hates[Charles, j]
);

% 4) Agatha hates everybody except the butler
constraint forall(j in Persons) (
    (j != Butler) -> hates[Agatha, j]
);
constraint hates[Agatha, Butler] = false;

% 5) The butler hates everyone not richer than Agatha
constraint forall(j in Persons) (
    (not richer[j, Agatha]) -> hates[Butler, j]
);

% 6) The butler hates everyone whom Agatha hates
constraint forall(j in Persons) (
    hates[Agatha, j] -> hates[Butler, j]
);

% 7) No one hates everyone
constraint forall(i in Persons) (
    exists(j in Persons) (not hates[i,j])
);

% 8) No one is richer than themselves
constraint forall(i in Persons) (
    not richer[i,i]
);

% 9) Richer relation is antisymmetric: if i richer than j then j not richer than i
constraint forall(i,j in Persons where i != j) (
    richer[i,j] -> not richer[j,i]
);

% 10) Richer relation is transitive
constraint forall(i,j,k in Persons) (
    (richer[i,j] /\ richer[j,k]) -> richer[i,k]
);

% 11) The victim is Agatha herself
constraint killer != Agatha \/ true; % just to emphasize killer is in Persons

solve satisfy;

output [
    "{",
    "\"killer\": ", show(killer),
    "}"
];
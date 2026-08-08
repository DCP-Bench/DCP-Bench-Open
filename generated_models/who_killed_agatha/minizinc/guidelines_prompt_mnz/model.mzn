
% Include necessary global constraints library
include "globals.mzn";

% Input data
int: N = 3;
array[1..N] of string: names = ["Agatha herself", "the butler", "Charles"];

% Decision variables
% who is the killer: 1=Agatha,2=butler,3=Charles
var 1..N: killer;
% wealth of each person
array[1..N] of var 1..3: w;
% hates[i,j] = true if person i hates person j (self-hate allowed)
array[1..N, 1..N] of var bool: hates;

% Constraints

% 1) Agatha hates everybody except the butler
constraint forall(j in 1..N) (
  if j == 2 then hates[1,j] = false else hates[1,j] = true endif
);

% 2) Charles hates no one that Agatha hates
constraint forall(j in 1..N) (
  hates[1,j] -> hates[3,j] = false
);

% 3) The butler hates everyone not richer than Aunt Agatha,
%    and also hates everyone whom Agatha hates.
constraint forall(j in 1..N) (
  hates[2,j] = ((w[j] <= w[1]) \/ hates[1,j])
);

% 4) No one hates everyone (i.e., each has at least one j with hates[i,j]=false)
constraint forall(i in 1..N) (
  sum(j in 1..N)(bool2int(hates[i,j])) < N
);

% 5) A killer always hates, and is no richer than, his victim (Agatha is victim)
constraint hates[killer,1] = true;
constraint w[killer] <= w[1];

% Solve: find the unique murderer
solve satisfy;

% Output result as JSON
output [
  "{",
    "\"killer\": " ++ show(killer),
  "}"
];

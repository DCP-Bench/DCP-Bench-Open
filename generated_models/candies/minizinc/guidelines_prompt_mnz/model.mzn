
% Include necessary global constraints library
include "globals.mzn";

% Input data
int: n = 9;
array[1..n] of int: ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4];

% Decision variables: candies for each child, at least 1 and at most n
array[1..n] of var 1..n: candies;

% Total candies
var int: z;

% Each child gets at least one candy
constraint forall(i in 1..n)(
  candies[i] >= 1
);

% Neighbour constraints: the higher-rated child must get more candies
constraint forall(i in 2..n)(
  if ratings[i] > ratings[i-1] then
    candies[i] > candies[i-1]
  elseif ratings[i] < ratings[i-1] then
    candies[i] < candies[i-1]
  else
    true
  endif
);

% Define total candies
constraint z = sum(i in 1..n)(candies[i]);

% Minimize the total number of candies
solve minimize z;

% Output result in JSON format with key "z"
output [
  "{",
    "\"z\": " ++ show(z),
  "}"
];

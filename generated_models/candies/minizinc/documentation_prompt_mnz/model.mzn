include "globals.mzn";

% Input data
array[1..9] of int: ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4];
int: n = length(ratings);

% Decision variables: candies given to each child
array[1..n] of var 1..n: candies;

% Constraints
% Each child must have at least 1 candy (already ensured by domain)
% If a child has a higher rating than the immediate neighbor, must have more candies
constraint
  forall(i in 1..n-1) (
    (ratings[i] > ratings[i+1]) -> (candies[i] > candies[i+1]) /\
    (ratings[i] < ratings[i+1]) -> (candies[i] < candies[i+1])
  );

% Objective: minimize total candies
var int: z = sum(i in 1..n)(candies[i]);
solve minimize z;

output [
  "{",
  "\"z\": ", show(z),
  "}"
];
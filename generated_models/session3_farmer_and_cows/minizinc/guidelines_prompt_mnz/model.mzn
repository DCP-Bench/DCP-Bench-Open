
% Include necessary global constraints library
include "globals.mzn";

% Data: number of sons and their required cow counts
set of int: SON = 0..4;
array[SON] of int: required_count = [7,6,5,4,3];
int: total_cows = sum(required_count);

% Sanity: total cows must be 25
constraint total_cows == 25;

% Decision variables: assign each cow i (1..25) to a son 0..4
array[1..25] of var SON: cow_assignments;

% 1) Each son k must receive exactly required_count[k] cows
constraint
  global_cardinality(cow_assignments,
                     [k | k in SON],
                     required_count);

% 2) Each son must receive cows summing to 65 kg (total milk 325/5)
int: target_milk = (1+25)*25 div 2 div 5; % = 65
constraint
  forall(k in SON) (
    sum(i in 1..25)( if cow_assignments[i] == k then i else 0 endif )
    == target_milk
  );

% Solve for any valid distribution
solve satisfy;

% Output the assignment as JSON
output [
  "{",
  "\"cow_assignments\":[" ++
    join(",", [ show(cow_assignments[i]) | i in 1..25 ]) ++
  "]",
  "}"
];

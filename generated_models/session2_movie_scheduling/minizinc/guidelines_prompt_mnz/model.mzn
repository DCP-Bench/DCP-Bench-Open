
include "globals.mzn";

% Input data
int: n = 9;
array[1..n] of int: start = [4, 17, 1, 12, 23, 9, 19, 2, 26];
array[1..n] of int: end   = [13, 27, 10, 18, 30, 16, 25, 7, 31];

% Decision variables: 1 if the movie is selected, 0 otherwise
array[1..n] of var 0..1: selected;

% No two overlapping movies can both be selected
constraint
  forall(i, j in 1..n where i < j /\ start[i] <= end[j] /\ start[j] <= end[i]) (
    selected[i] + selected[j] <= 1
  );

% Objective: maximize the number of selected movies
var int: num_selected_movies = sum(i in 1..n)(selected[i]);
solve maximize num_selected_movies;

% Output in JSON format
output [
  "{",
    "\"num_selected_movies\": " ++ show(num_selected_movies) ++ ",",
    "\"selected_movies\": [" ++
      join(",", [ show(selected[i]) | i in 1..n ]) ++
    "]",
  "}"
];

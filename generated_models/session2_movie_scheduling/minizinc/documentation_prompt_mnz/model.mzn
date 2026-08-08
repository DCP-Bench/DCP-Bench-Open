include "globals.mzn";

% Input data
int: n = 9;
array[1..n] of string: titles = [
    "Tarjan of the Jungle",
    "The Four Volume Problem",
    "The President's Algorist",
    "Steiner's Tree",
    "Process Terminated",
    "Halting State",
    "Programming Challenges",
    "Discrete Mathematics",
    "Calculated Bets"
];
array[1..n] of int: start_days = [4, 17, 1, 12, 23, 9, 19, 2, 26];
array[1..n] of int: end_days = [13, 27, 10, 18, 30, 16, 25, 7, 31];

% Decision variables
array[1..n] of var 0..1: selected_movies;

% Constraints
% No two selected movies can overlap in their filming intervals
constraint
    forall(i, j in 1..n where i < j) (
        (selected_movies[i] == 1 /\ selected_movies[j] == 1) ->
        (end_days[i] < start_days[j] \/ end_days[j] < start_days[i])
    );

% Objective: maximize the number of selected movies
var int: num_selected_movies = sum(i in 1..n)(selected_movies[i]);

solve maximize num_selected_movies;

output [
    "{",
    "\"num_selected_movies\": ", show(num_selected_movies), ",",
    "\"selected_movies\": ", show(selected_movies),
    "}"
];
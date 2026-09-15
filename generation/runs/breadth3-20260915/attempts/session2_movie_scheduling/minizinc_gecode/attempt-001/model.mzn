include "globals.mzn";

% Each row of movies is a title with a start and an end, so the field mixes a
% string with two integers in one row.
array[int, int] of int: movies;

set of int: Movies = index_set_1of2(movies);
array[Movies] of var bool: selected_movies;

constraint forall(i, j in Movies where i != j
                  /\ movies[i, 3] > movies[j, 2] /\ movies[j, 3] > movies[i, 2]) (
    bool2int(selected_movies[i]) + bool2int(selected_movies[j]) <= 1);

var int: objective = sum(i in Movies) (bool2int(selected_movies[i]));
solve maximize objective;

output ["{\"selected_movies\": [", join(", ", [show(selected_movies[i]) | i in Movies]), "]}"];

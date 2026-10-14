% Movie scheduling: an actor accepts the largest set of film offers whose
% filming periods (first to last day, inclusive) do not overlap.

% each movie is [title, start, end]; the runner binds the mixed-type rows as
% one array per column
array[int] of string: movies_1;   % title (not used by the model)
array[int] of int: movies_2;      % first day of filming
array[int] of int: movies_3;      % last day of filming

set of int: Movie = index_set(movies_2);

% selected_movies[i] is true if the offer for movie i is accepted
array[Movie] of var bool: selected_movies;

% two movies whose filming periods share a day cannot both be accepted
constraint forall(i, j in Movie where i < j
                  /\ movies_3[i] >= movies_2[j] /\ movies_3[j] >= movies_2[i])(
  not (selected_movies[i] /\ selected_movies[j])
);

% every film pays the same fee, so maximise the number of accepted movies
var int: objective = sum(i in Movie)(bool2int(selected_movies[i]));
solve maximize objective;

output ["{\"selected_movies\": [", join(", ", [show(selected_movies[i]) | i in Movie]), "]}"];

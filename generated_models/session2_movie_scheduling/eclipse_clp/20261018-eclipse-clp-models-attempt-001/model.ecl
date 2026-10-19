% Movie scheduling: an actor is offered n films, each with a first and last day
% of filming. Select the largest set of films whose filming intervals do not
% overlap. Output selected_movies[i] = 1 when film i is accepted.

:- lib(ic).

model(Instance, Sel, [selected_movies-Sel], max(sum(Sel))) :-
    memberchk(movies-Movies, Instance),
    length(Movies, N),
    length(Sel, N),
    Sel :: 0..1,
    ( foreach([_, S, E], Movies), foreach(S-E, Ivs) do true ),
    % Two films whose filming intervals overlap cannot both be accepted, since
    % the actor must be available throughout each interval.
    conflicts(Ivs, Sel).

% Post the pairwise conflicts of the first film with all later films, then recurse.
conflicts([], _).
conflicts([S1-E1|Rest], [X|Xs]) :-
    post_conflicts(Rest, Xs, S1, E1, X),
    conflicts(Rest, Xs).

post_conflicts([], [], _, _, _).
post_conflicts([S2-E2|Rest], [Y|Ys], S1, E1, X) :-
    (   S1 =< E2, S2 =< E1
    ->  X + Y #=< 1
    ;   true
    ),
    post_conflicts(Rest, Ys, S1, E1, X).

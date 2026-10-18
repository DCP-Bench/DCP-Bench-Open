% Candies: give each child in a line at least one candy, give more candies to a
% child with a higher rating than to an immediate neighbour, and minimise the total.
% Output: x (candies per child) and z (total number of candies).

:- lib(ic).

model(Instance, Xs, [x-Xs, z-Z], min(Z)) :-
    memberchk(ratings-Rs, Instance),
    length(Rs, N),
    length(Xs, N),
    % each child gets at least 1 candy; no child needs more than N candies in an
    % optimal allocation, since the chain of higher-rated neighbours is at most N long
    Xs :: 1..N,
    % the total number of candies is the sum over all children
    Z #= sum(Xs),
    % if two children sit next to each other, the one with the higher rating must
    % get more candies (equal ratings give no constraint)
    neighbour_constraints(Rs, Xs).

% if two children sit next to each other, the one with the higher rating must
% get more candies than the other
neighbour_constraints([], []).
neighbour_constraints([_], [_]).
neighbour_constraints([R1, R2 | Rs], [X1, X2 | Xs]) :-
    (   R1 > R2 -> X1 #> X2
    ;   R1 < R2 -> X1 #< X2
    ;   true
    ),
    neighbour_constraints([R2 | Rs], [X2 | Xs]).

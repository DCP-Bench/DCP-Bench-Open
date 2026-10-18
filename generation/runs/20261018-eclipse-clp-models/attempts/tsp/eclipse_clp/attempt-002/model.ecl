% Travelling salesman problem: given a list of cities with their locations,
% find the shortest route that visits each city exactly once and returns to
% the origin city. The distance between two points is the Euclidean distance
% rounded to an integer. Output: the optimal travel distance (travel_distance).
% Same model as attempt 1, on the Gecode solver (gfd) for its circuit/1 and
% element/3 propagation.

:- lib(gfd).
:- lib(listut).

% Build the N x N matrix of rounded Euclidean distances from the locations.
% The sqrt of an integer is never exactly k+0.5, so floor(x+0.5) is the rounding.
model(Instance, Next, [travel_distance-Cost], min(Cost)) :-
    memberchk(locations-Locs, Instance),
    length(Locs, N),
    dist_matrix(Locs, Rows),

    % Visit each city exactly once and return to the origin city: the
    % successors form a single cycle through all cities, and Next[I] is the
    % city visited after city I, so no city is followed by itself.
    length(Next, N),
    Next :: 1..N,
    circuit(Next),
    ( for(I, 1, N), foreach(Nx, Next), foreach(Row, Rows), foreach(D, Ds) do
        Nx #\= I,
        element(Nx, Row, D)
    ),

    % The travel distance is the sum of the distances of the route, the
    % distance between two cities being the Euclidean distance rounded to an
    % integer.
    Cost #= sum(Ds),
    Cost :: 0..100000.

pair_dist([X1, Y1], [X2, Y2], D) :-
    DX is X1 - X2,
    DY is Y1 - Y2,
    D is integer(floor(sqrt(DX * DX + DY * DY) + 0.5)).

dist_matrix(Locs, Rows) :-
    ( foreach(P, Locs), foreach(Row, Rows), param(Locs) do
        ( foreach(Q, Locs), foreach(D, Row), param(P) do
            pair_dist(P, Q, D)
        )
    ).

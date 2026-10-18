% Travelling salesman problem: given a list of cities with their locations,
% find the shortest route that visits each city exactly once and returns to
% the origin city. The distance between two points is the Euclidean distance
% rounded to an integer. Output: the optimal travel distance (travel_distance).
% Successor model on ic. Extra (implied) work: a rank view that tries the
% nearest neighbour first, and a predecessor view with an incoming-leg sum.

:- lib(ic).

model(Instance, Ranks, [travel_distance-Cost], min(Cost)) :-
    memberchk(locations-Locs, Instance),
    length(Locs, N),
    N1 is N - 1,
    dist_matrix(Locs, Rows),

    % Visit each city exactly once and return to the origin city: the
    % successors form a single cycle through all cities, Next[I] is the city
    % visited after city I, and no city is followed by itself.
    length(Next, N),
    Next :: 1..N,
    circuit(Next),

    % The distance of the leg leaving city I: rank R of the successor among the
    % other cities sorted by distance from I (rank 1 is the nearest city).
    length(Ranks, N),
    Ranks :: 1..N1,
    ( for(I, 1, N), foreach(R, Ranks), foreach(Nx, Next), foreach(Dout, Douts),
      foreach(Row, Rows), param(N) do
        sorted_others(Row, I, N, SCities, SDists),
        element(R, SCities, Nx),
        element(R, SDists, Dout)
    ),

    % The route enters each city once: Prev[J] is the city visited before
    % city J, linked to Next by a 0/1 matrix (implied constraint).
    length(Prev, N),
    Prev :: 1..N,
    ( for(J, 1, N), foreach(P, Prev), foreach(Row2, Rows), foreach(Din, Dins),
      param(N) do
        P #\= J,
        element(P, Row2, Din)
    ),
    ( for(I, 1, N), foreach(Nx2, Next), param(N, Prev) do
        ( for(J, 1, N), foreach(Pj, Prev), param(I, Nx2) do
            ( I =:= J
            -> true
            ;  B #= (Nx2 #= J),
               B #= (Pj #= I)
            )
        )
    ),

    % The travel distance is the sum of the distances of the route, the
    % distance between two cities being the Euclidean distance rounded to an
    % integer; it can be summed over outgoing legs or over incoming legs.
    Cost #= sum(Douts),
    Cost #= sum(Dins).

% Nearest neighbour first, smallest domain first.
search_goal(Ranks) :-
    search(Ranks, 0, first_fail, indomain_min, complete, []).

% The other cities of city I sorted by (distance, index), with their distances.
sorted_others(Row, I, N, SCities, SDists) :-
    ( for(J, 1, N), foreach(D, Row), fromto([], A, B, Pairs), param(I) do
        ( J =:= I -> B = A ; B = [D-J|A] )
    ),
    msort(Pairs, Sorted),
    ( foreach(D1-J1, Sorted), foreach(D1, SDists), foreach(J1, SCities) do true ).

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

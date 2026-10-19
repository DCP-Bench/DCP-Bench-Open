% csplib_009 perfect square placement: pack squares with the given integer sides
% into a bigger square of side base, so that no squares overlap, all borders are
% parallel to the border of the big square, and there is no spare capacity.
% Outputs x_coords and y_coords: the lower-left corner of each square, starting from 0.
% Solver: gfd (Gecode), so the cumulative and the reified disjunctions are Gecode's.

:- lib(gfd).

model(Instance, Vars, [x_coords-Xs, y_coords-Ys], none) :-
    memberchk(base-B, Instance),
    memberchk(sides-Sides, Instance),
    length(Sides, N),
    length(Xs, N),
    length(Ys, N),
    % each square lies inside the big square: its corner ranges over 0..base-side
    ( foreach(S, Sides), foreach(X, Xs), foreach(Y, Ys), param(B) do
        Hi is B - S,
        X :: 0..Hi,
        Y :: 0..Hi
    ),
    append(Xs, Ys, Vars),
    % squares do not overlap: for each pair, one lies left of, right of, below or above the other
    square_list(Xs, Ys, Sides, Squares),
    no_overlap_all(Squares),
    % redundant: the squares crossing any vertical line have sides summing to at most base,
    % and likewise for any horizontal line
    cumulative(Xs, Sides, Sides, B),
    cumulative(Ys, Sides, Sides, B).

% the squares as a list of placed(X, Y, Side) terms
square_list([], [], [], []).
square_list([X|Xs], [Y|Ys], [S|Ss], [placed(X, Y, S)|Rest]) :-
    square_list(Xs, Ys, Ss, Rest).

% each square against every later square
no_overlap_all([]).
no_overlap_all([placed(X1, Y1, S1)|Rest]) :-
    ( foreach(placed(X2, Y2, S2), Rest), param(X1, Y1, S1) do
        ( X1 + S1 #=< X2 ) or ( X2 + S2 #=< X1 ) or ( Y1 + S1 #=< Y2 ) or ( Y2 + S2 #=< Y1 )
    ),
    no_overlap_all(Rest).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

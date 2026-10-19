% Schur's lemma (CSPLib 015): put the balls 1..n into c boxes so that for any
% triple of balls (x, y, z) with x + y = z, not all three are in the same box.

:- lib(ic).
:- lib(listut).

model(Instance, Balls, [balls-Balls]) :-
    memberchk(n-N, Instance),
    memberchk(c-C, Instance),
    length(Balls, N),
    Balls :: 1..C,
    % Boolean M(i,j) is 1 exactly when ball i is in box j.
    ( foreach(B, Balls), foreach(Row, Rows), param(C) do
        boxes_of(B, 1, C, Row)
    ),
    % For any triple of balls (x, y, z) with x + y = z, not all three are in the same box.
    post_x(1, N, Rows).

% boxes_of(+Ball, +J, +C, -Ms): Ms holds, for boxes J..C, the booleans "Ball is in box j".
boxes_of(B, J, C, Ms) :-
    ( J > C ->
        Ms = []
    ;   Ms = [M|Ms1],
        M #= (B #= J),
        J1 is J + 1,
        boxes_of(B, J1, C, Ms1)
    ).

% Triples x <= y with z = x + y <= N.
post_x(X, N, Rows) :-
    ( X > N ->
        true
    ;   post_y(X, X, N, Rows),
        X1 is X + 1,
        post_x(X1, N, Rows)
    ).

post_y(X, Y, N, Rows) :-
    ( Y > N ->
        true
    ;   Z is X + Y,
        ( Z =< N ->
            post_triple(X, Y, Z, Rows)
        ;   true
        ),
        Y1 is Y + 1,
        post_y(X, Y1, N, Rows)
    ).

% In every box, at most two of the three balls x, y, z are present.
post_triple(X, Y, Z, Rows) :-
    nth1(X, Rows, RX),
    nth1(Y, Rows, RY),
    nth1(Z, Rows, RZ),
    ( foreach(Mx, RX), foreach(My, RY), foreach(Mz, RZ) do
        Mx + My + Mz #=< 2
    ).

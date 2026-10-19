% Balanced Incomplete Block Design (BIBD), CSPLib 028.
% Find a v by b incidence matrix (v objects, b blocks) of 0s and 1s such that
% each block contains exactly k objects, each object occurs in exactly r blocks,
% and every two distinct objects occur together in exactly lambda blocks.

:- lib(ic).
:- lib(listut).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

model(Instance, Vars, [matrix-Rows], none) :-
    memberchk(v-V, Instance),
    memberchk(b-B, Instance),
    memberchk(r-R, Instance),
    memberchk(k-K, Instance),
    memberchk(l-L, Instance),
    length(Rows, V),
    ( foreach(Row, Rows), param(B) do
        length(Row, B),
        Row :: 0..1
    ),
    flatten(Rows, Vars),

    % each object occurs in exactly r blocks (row sums)
    ( foreach(Row, Rows), param(R) do
        sum(Row) #= R
    ),

    % each block contains exactly k objects (column sums)
    ( for(C, 1, B), param(Rows, K) do
        column(Rows, C, Col),
        sum(Col) #= K
    ),

    % every two distinct objects occur together in exactly lambda blocks
    pairwise_lambda(Rows, L).

% column(+Rows, +C, -Col): the C-th entry of every row, in row order
column(Rows, C, Col) :-
    ( foreach(Row, Rows), foreach(X, Col), param(C) do
        nth1(C, Row, X)
    ).

% any two distinct rows share exactly L blocks (scalar product of 0/1 rows)
pairwise_lambda([], _).
pairwise_lambda([Row|Rows], L) :-
    ( foreach(Other, Rows), param(Row, L) do
        common_blocks(Row, Other, L)
    ),
    pairwise_lambda(Rows, L).

common_blocks(Row1, Row2, L) :-
    ( foreach(X, Row1), foreach(Y, Row2), foreach(P, Ps) do
        P #= X * Y
    ),
    sum(Ps) #= L.

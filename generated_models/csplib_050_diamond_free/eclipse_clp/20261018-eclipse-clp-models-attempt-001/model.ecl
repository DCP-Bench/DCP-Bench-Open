% csplib_050_diamond_free: diamond-free graph with a given degree sequence.
%
% Given N, find a simple undirected graph on the vertices 1..N whose degree sequence
% d_1 >= d_2 >= ... >= d_N has every degree greater than zero and divisible by 3, whose
% degree sum is divisible by 12, and which has no diamond (no four vertices spanning
% at least five edges). Output: the adjacency matrix, as 0/1 leaves read as Booleans.

:- lib(ic).
:- lib(lists).
:- lib(listut).

model(Instance, Vars, [matrix-Rows], none) :-
    memberchk('N'-N, Instance),
    length(Rows, N),
    % The adjacency matrix holds 0 or 1 in every cell.
    matrix_domains(Rows, N),
    % A simple graph has no loop edges, and an edge {u,v} is one entry seen from both ends.
    simple_undirected(1, N, Rows),
    flatten(Rows, Vars),
    % Each degree is greater than zero and divisible by 3, so d_i = 3 * D_i with D_i >= 1.
    MaxD is (N - 1) // 3,
    degree_variables(Rows, Ds, MaxD),
    % The degrees are ordered: d_i >= d_{i+1}.
    ordered_desc(Ds),
    % The sum of the degrees is divisible by 12, that is, sum(D_i) is divisible by 4.
    sum(Ds) #= 4 * Q,
    MaxSum is N * MaxD,
    Q :: 0..MaxSum,
    % A diamond is four vertices with at least five edges between them; a diamond-free
    % graph has at most four edges among any four vertices.
    no_diamonds(Rows, N).

matrix_domains([], _).
matrix_domains([Row|Rows], N) :-
    length(Row, N),
    Row :: 0..1,
    matrix_domains(Rows, N).

% Row I has a 0 on the diagonal, and entry (I,J) equals entry (J,I).
simple_undirected(I, N, _) :- I > N, !.
simple_undirected(I, N, Rows) :-
    nth1(I, Rows, RowI),
    nth1(I, RowI, 0),
    I1 is I + 1,
    symmetric_from(I1, I, N, Rows),
    simple_undirected(I1, N, Rows).

symmetric_from(J, _, N, _) :- J > N, !.
symmetric_from(J, I, N, Rows) :-
    nth1(I, Rows, RowI),
    nth1(J, Rows, RowJ),
    nth1(J, RowI, X),
    nth1(I, RowJ, X),
    J1 is J + 1,
    symmetric_from(J1, I, N, Rows).

% Each degree is 3 * D_i, where the row sum is the degree of that vertex.
degree_variables([], [], _).
degree_variables([Row|Rows], [D|Ds], MaxD) :-
    D :: 1..MaxD,
    sum(Row) #= 3 * D,
    degree_variables(Rows, Ds, MaxD).

% The degrees are non-increasing.
ordered_desc([]).
ordered_desc([_]) :- !.
ordered_desc([D1, D2|Ds]) :-
    D1 #>= D2,
    ordered_desc([D2|Ds]).

% Diamond-free: among any four vertices A < B < C < D at most four of the six edges are present.
no_diamonds(Rows, N) :-
    N4 is N - 3,
    ( for(A, 1, N4), param(Rows, N) do
        A1 is A + 1,
        N3 is N - 2,
        ( for(B, A1, N3), param(Rows, N, A) do
            B1 is B + 1,
            N2 is N - 1,
            ( for(C, B1, N2), param(Rows, N, A, B) do
                C1 is C + 1,
                ( for(D, C1, N), param(Rows, A, B, C) do
                    no_diamond4(Rows, A, B, C, D)
                )
            )
        )
    ).

no_diamond4(Rows, A, B, C, D) :-
    edge(Rows, A, B, X1), edge(Rows, A, C, X2), edge(Rows, A, D, X3),
    edge(Rows, B, C, X4), edge(Rows, B, D, X5), edge(Rows, C, D, X6),
    X1 + X2 + X3 + X4 + X5 + X6 #=< 4.

edge(Rows, I, J, X) :-
    nth1(I, Rows, RowI),
    nth1(J, RowI, X).

% CSPLib 074, maximum clique.
% Given a simple undirected graph G = (V, E), find a clique of largest size: a subset of
% vertices where every two distinct vertices are adjacent. Output c, a binary array of
% length n, with c[i] = 1 when vertex i is in the maximum clique, 0 otherwise.
% Vertices are 0-based indices into the adjacency matrix adj.

:- lib(ic).
:- lib(listut).

model(Instance, Cs, [c-Cs], max(sum(Cs))) :-
    memberchk(n-N, Instance),
    memberchk(adj-Adj, Instance),
    length(Cs, N),
    Cs :: 0..1,
    % Every two distinct vertices of the clique are adjacent: two vertices that are
    % not adjacent cannot both be selected.
    clique_pairs(0, N, Adj, Cs).

% Walk over the rows I of the adjacency matrix.
clique_pairs(I, N, Adj, Cs) :-
    (   I >= N
    ->  true
    ;   J is I + 1,
        clique_row(I, J, N, Adj, Cs),
        I1 is I + 1,
        clique_pairs(I1, N, Adj, Cs)
    ).

% For a fixed I, walk over the columns J > I.
clique_row(I, J, N, Adj, Cs) :-
    (   J >= N
    ->  true
    ;   nth0(I, Adj, RowI),
        nth0(J, RowI, A),
        (   A =:= 0
        ->  nth0(I, Cs, CI),
            nth0(J, Cs, CJ),
            CI + CJ #=< 1
        ;   true
        ),
        J1 is J + 1,
        clique_row(I, J1, N, Adj, Cs)
    ).

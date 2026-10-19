% Maximal independent set on a graph given by its adjacency lists (1-based,
% symmetric). Find a set of nodes, no two of which are adjacent, such that
% no further node can be added. Output nodes(I) = 1 when node I is in the set.

:- lib(ic).
:- lib(listut).

model(Instance, Xs, [nodes-Xs]) :-
    memberchk(n-N, Instance),
    memberchk(adjacency_list-Adj, Instance),
    length(Xs, N),
    Xs :: 0..1,

    % no two of which are adjacent
    ( for(I, 1, N), param(Adj, Xs) do
        nth1(I, Adj, Row),
        nth1(I, Xs, XI),
        ( foreach(J, Row), param(XI, Xs) do
            nth1(J, Xs, XJ),
            XI + XJ #=< 1
        )
    ),

    % not a subset of any other independent set: every node that is not
    % in the set has a neighbour in it (a node in the set satisfies this
    % trivially, since it contributes 1 to the left-hand side)
    ( for(I, 1, N), param(Adj, Xs) do
        nth1(I, Adj, Row),
        nth1(I, Xs, XI),
        ( foreach(J, Row), foreach(XJ, Ys), param(Xs) do
            nth1(J, Xs, XJ)
        ),
        XI + sum(Ys) #>= 1
    ).

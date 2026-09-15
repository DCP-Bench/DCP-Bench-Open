:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Maximal independent set: no edge has both ends selected, and no node could
% be added without breaking that.
model(Instance, Nodes, [nodes-Nodes]) :-
    N = Instance.n,
    Adjacency = Instance.adjacency_list,
    length(Nodes, N),
    Nodes ins 0..1,
    Last is N - 1,
    numlist(0, Last, Indices),
    maplist({Nodes, Adjacency}/[I]>>node_rules(Nodes, Adjacency, I), Indices).

node_rules(Nodes, Adjacency, I) :-
    nth0(I, Nodes, Here),
    nth0(I, Adjacency, Neighbours),
    maplist({Nodes, Here, I}/[Neighbour]>>
                independent(Nodes, Here, I, Neighbour),
            Neighbours),
    % Maximality: every node is selected or has a selected neighbour.
    maplist({Nodes}/[Neighbour, There]>>
                (J is Neighbour - 1, nth0(J, Nodes, There)),
            Neighbours, Theirs),
    sum([Here|Theirs], #>=, 1).

% Independence.  The adjacency list is 1-based; each edge is seen from both
% ends, so only i < j is posted.
independent(Nodes, Here, I, Neighbour) :-
    J is Neighbour - 1,
    (   I < J
    ->  nth0(J, Nodes, There),
        Here + There #=< 1
    ;   true
    ).

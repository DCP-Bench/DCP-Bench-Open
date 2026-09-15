:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Maximum clique: pick as many vertices as possible, no two of them
% non-adjacent.
model(Instance, Chosen, [c-Chosen], max(Size)) :-
    N = Instance.n,
    Adj = Instance.adj,
    length(Chosen, N),
    Chosen ins 0..1,
    Last is N - 1,
    numlist(0, Last, Vertices),
    maplist({Chosen, Adj, Last}/[I]>>
                non_adjacent_pairs(Chosen, Adj, Last, I),
            Vertices),
    sum(Chosen, #=, Size).

non_adjacent_pairs(Chosen, Adj, Last, I) :-
    Next is I + 1,
    (   Next > Last
    ->  true
    ;   numlist(Next, Last, Others),
        nth0(I, Chosen, Here),
        nth0(I, Adj, Row),
        maplist({Chosen, Row, Here}/[J]>>forbid_pair(Chosen, Row, Here, J),
                Others)
    ).

forbid_pair(Chosen, Row, Here, J) :-
    nth0(J, Row, Edge),
    (   Edge =:= 0
    ->  nth0(J, Chosen, There),
        Here + There #=< 1
    ;   true
    ).

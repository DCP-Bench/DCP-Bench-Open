% Broken weights: a merchant's measuring weight broke into n pieces, each a whole
% number of pounds. The pieces must weigh every integral weight from 1 to the total
% weight m, with pieces placed on either side of a balance scale.
:- lib(ic).

model(Instance, Weights, [weights-Weights]) :-
    memberchk(m-M, Instance),
    memberchk(n-N, Instance),
    length(Weights, N),

    % the pieces are whole pounds and together weigh the total m
    Weights :: 1..M,
    sum(Weights) #= M,

    % every integral weight k from 1 to the total weight can be balanced:
    % each piece is on the left (-1), on the right (+1) or off the scale (0)
    ( for(K, 1, M), param(Weights, N) do
        length(Cs, N),
        Cs :: -1..1,
        ( foreach(C, Cs), foreach(W, Weights), foreach(T, Ts) do
            T #= C * W
        ),
        sum(Ts) #= K
    ).

search_goal(Weights) :-
    search(Weights, 0, first_fail, indomain_min, complete, []).

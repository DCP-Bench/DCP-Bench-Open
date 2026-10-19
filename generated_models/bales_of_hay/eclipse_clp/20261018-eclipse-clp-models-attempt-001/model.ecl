% Bales of hay: n bales were weighed in all possible combinations of two,
% and the pair weights, in numerical order, are given. Find the weight of
% each bale.
:- lib(ic).
:- lib(listut).

model(Instance, Vars, [bales-Bales], none) :-
    memberchk(n-N, Instance),
    memberchk(weights-WList, Instance),
    length(WList, M),
    M =:= N * (N - 1) // 2,
    ( foreach(W, WList), fromto(0, A, B, Max) do B is max(A, W) ),

    % Each bale weighs between 0 and the heaviest pair weight.
    length(Bales, N),
    Bales :: 0..Max,

    % The bales were weighed in all possible combinations of two, one
    % weighing per pair of bales.
    all_pairs(N, Pairs),

    % The weights were arranged in numerical order, without keeping track
    % of which weight matched which pair: each pair takes a different weight.
    length(Idx, M),
    Idx :: 1..M,
    alldifferent(Idx),
    post_pairs(Pairs, Idx, Bales, WList),

    append(Bales, Idx, Vars).

% The pairs I-J with 1 =< I < J =< N, in order.
all_pairs(N, Ps) :- all_pairs(1, N, Ps, []).
all_pairs(I, N, Ps, Tail) :- I >= N, !, Ps = Tail.
all_pairs(I, N, Ps, Tail) :-
    J0 is I + 1,
    pair_row(I, J0, N, Ps, Mid),
    I1 is I + 1,
    all_pairs(I1, N, Mid, Tail).

pair_row(_, J, N, Ps, Tail) :- J > N, !, Ps = Tail.
pair_row(I, J, N, [I-J | Ps], Tail) :-
    J1 is J + 1,
    pair_row(I, J1, N, Ps, Tail).

% The weight of a pair of bales is the sum of the two bales.
post_pairs([], [], _, _).
post_pairs([I-J | Ps], [X | Xs], Bales, WList) :-
    nth1(I, Bales, Bi),
    nth1(J, Bales, Bj),
    S #= Bi + Bj,
    element(X, WList, S),
    post_pairs(Ps, Xs, Bales, WList).

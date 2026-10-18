% coin3_application: find the minimum number of coins that allows one to pay exactly
% any amount smaller than a given maximum amount, using a given set of denominations.
% Output x: the number of each type of coin used.

:- lib(ic).
:- lib(listut).

model(Instance, Xs, [x-Xs], min(sum(Xs))) :-
    memberchk(denominations-Ds, Instance),
    memberchk(max_amount_to_pay-M, Instance),
    Top is M - 1,
    % the number of coins of each denomination used; more coins of one denomination
    % than the largest amount divided by it are never part of a minimum
    ( foreach(D, Ds), foreach(X, Xs), param(Top) do
        MaxC is Top // D,
        X :: 0..MaxC
    ),
    % every amount smaller than the maximum amount can be paid exactly
    length(Zeros, Top),
    ( foreach(Z, Zeros) do Z = 0 ),
    chain(Ds, Xs, [1 | Zeros], Top).

% Q(A) is 1 when amount A can be paid with the coins treated so far. Before any coin
% only amount 0 can be paid. Adding a denomination D with count X: N(A) is the fewest
% coins of D that, with the earlier coins, pay A (capped at Cap), and A is payable
% with the new coins when N(A) =< X.
chain([], [], [_ | Rest], _) :-
    ( foreach(Q, Rest) do Q #= 1 ).
chain([D | Ds], [X | Xs], Qprev, Top) :-
    level(D, X, Top, Qprev, Qnext),
    chain(Ds, Xs, Qnext, Top).

level(D, X, Top, Qprev, Qnext) :-
    Cap is Top // D + 1,
    Len is Top + 1,
    length(Ns, Len),
    Ns :: 0..Cap,
    ( for(A, 0, Top), foreach(Qp, Qprev), foreach(N, Ns), foreach(Qb, Qnext),
      param(D, X, Cap, Ns) do
        level_amount(A, D, X, Cap, Qp, Ns, N, Qb)
    ).

% the fewest coins of denomination D that pay amount A: none when A is already
% payable, otherwise one more than the fewest that pay A - D
level_amount(A, D, X, Cap, Qp, Ns, N, Qb) :-
    Qb :: 0..1,
    Qb #= (N #=< X),
    (Qp #= 1) => (N #= 0),
    ( A >= D ->
        Prev is A - D + 1,
        nth1(Prev, Ns, NPrev),
        (Qp #= 0) => (N #= min(Cap, 1 + NPrev))
    ;
        (Qp #= 0) => (N #= Cap)
    ).

:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Age changing: the same four operations, applied in two different orders, turn
% each spouse's age into the other's.  The operations are +2, /8, -3 and *7,
% numbered in that order; the division is stated as a multiplication so that
% only exact eighths count, as the reference does.
model(_Instance, Vars, [m-M, h-H]) :-
    [M, H] ins 16..120,
    length(Perm1, 4), Perm1 ins 0..3, all_distinct(Perm1),
    length(Perm2, 4), Perm2 ins 0..3, all_distinct(Perm2),
    length(MList, 5), MList ins 1..1000,
    length(HList, 5), HList ins 1..1000,
    append([[M, H], Perm1, Perm2, MList, HList], Vars),

    % The same operations, but in a different order.
    maplist([P, Q, B]>>(P #\= Q #<==> B), Perm1, Perm2, Differs),
    sum(Differs, #=, DiffCount),
    DiffCount #> 0,

    % Start from my age and finish at my husband's, and the other way round.
    HList = [FirstH|_], FirstH #= M,
    last(HList, LastH), LastH #= H,
    MList = [FirstM|_], FirstM #= H,
    last(MList, LastM), LastM #= M,

    apply_chain(Perm1, HList),
    apply_chain(Perm2, MList).

apply_chain([], [_]).
apply_chain([Op|Ops], [Old, New|Rest]) :-
    check(Op, Old, New),
    apply_chain(Ops, [New|Rest]).

check(Op, Old, New) :-
    Op #= 0 #==> New #= Old + 2,
    Op #= 1 #==> 8 * New #= Old,
    Op #= 2 #==> New #= Old - 3,
    Op #= 3 #==> New #= Old * 7.

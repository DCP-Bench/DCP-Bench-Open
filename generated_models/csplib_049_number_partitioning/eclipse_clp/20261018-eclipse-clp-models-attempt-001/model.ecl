% Number partitioning (CSPLib 049): partition the numbers 1..N into two sets
% A and B such that A and B have the same cardinality, the same sum and the
% same sum of squares. Each set is printed in increasing order.

:- lib(ic).

model(Instance, Vars, [ 'A'-Av, 'B'-Bv ]) :-
    memberchk(n-N, Instance),
    N mod 2 =:= 0,
    K is N // 2,
    length(Av, K),
    length(Bv, K),
    append(Av, Bv, Vars),

    % The numbers 1..N are partitioned into A and B
    Vars :: 1..N,
    alldifferent(Vars),

    % A and B have the same cardinality
    % (length(Av) = length(Bv) = N/2 by construction)

    % Sum of numbers in A = sum of numbers in B
    sum(Av) #= sum(Bv),

    % Sum of squares of numbers in A = sum of squares of numbers in B
    sq_sum(Av, 0, SqA),
    sq_sum(Bv, 0, SqB),
    SqA #= SqB,

    % Print each set in increasing order
    increasing(Av),
    increasing(Bv).

sq_sum([], S, S).
sq_sum([X|Xs], S0, S) :-
    S1 #= S0 + X*X,
    sq_sum(Xs, S1, S).

increasing([]).
increasing([_]).
increasing([X,Y|T]) :-
    X #< Y,
    increasing([Y|T]).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

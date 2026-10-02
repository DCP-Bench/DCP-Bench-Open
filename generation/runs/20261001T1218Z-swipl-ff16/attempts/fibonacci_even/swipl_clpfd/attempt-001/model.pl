:- use_module(library(clpfd)).
:- use_module(library(apply)).

% Even Fibonacci sum (Project Euler 2): add up the even-valued terms of the
% Fibonacci sequence that do not exceed four million. The problem has no
% instance data; the term count, the limit and the variable bounds below are
% the ones the reference fixes.
model(_Instance, Vars, [res-Res]) :-
    N = 35,                       % terms f[0]..f[N], enough to pass the limit
    Limit = 4000000,              % only terms below this are summed
    MaxTerm = 10000000,           % upper bound of every term, as in the reference
    MaxSum = 100000000,           % upper bound of the sum, as in the reference

    % Fib[i] is the i-th Fibonacci number, Counted[i] says whether Fib[i] is
    % part of the sum
    Len is N + 1,
    length(Fib, Len), Fib ins 0..MaxTerm,
    length(Counted, Len), Counted ins 0..1,
    Res in 0..MaxSum,

    % the sequence starts 0, 1, 1 and every later term is the sum of the two
    % terms before it
    Fib = [F0, F1, F2|_],
    F0 #= 0, F1 #= 1, F2 #= 1,
    Fib = [_|FibFromOne],
    fibonacci_steps(FibFromOne),

    % the term f[0] is never counted
    Counted = [X0|CountedFromOne],
    X0 #= 0,

    % a term is counted exactly when it is even and below the limit
    maplist(counted_if_even_below(Limit), FibFromOne, CountedFromOne),

    % the answer is the sum of the counted terms f[1]..f[N]
    maplist(weighted, CountedFromOne, FibFromOne, Weighted),
    sum(Weighted, #=, Res),

    % the starting terms fix every entry of Fib and Counted, so only Res is
    % left to label; all are listed anyway
    append([[Res], Fib, Counted], Vars).

% f[i] = f[i-1] + f[i-2] for every window of three consecutive terms
fibonacci_steps([A, B, C|Rest]) :-
    C #= A + B,
    fibonacci_steps([B, C|Rest]).
fibonacci_steps([_, _]).

% X is 1 exactly when the term F is even and below Limit
counted_if_even_below(Limit, F, X) :-
    (F mod 2 #= 0 #/\ F #< Limit) #<==> X.

% a counted term contributes its value, an uncounted one contributes 0
weighted(X, F, P) :-
    P #= X * F.

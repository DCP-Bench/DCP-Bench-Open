:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% CMO 2012 problem: find two positive integers a and b such that a - b is a
% prime number and a * b is a perfect square n^2, with a the smallest value
% not below a given minimum.
model(Instance, Vars, [a-A, b-B, n-N, p-P], min(A)) :-
    MinA = Instance.min_a,       % a must be at least this
    MaxVal = Instance.max_val,   % upper bound for all four numbers

    % the primes below max_val, as a domain for p = a - b
    Limit is MaxVal - 1,
    findall(Prime, (between(2, Limit, Prime), is_prime(Prime)), Primes),
    domain_of(Primes, PrimeDomain),

    A in MinA..MaxVal,
    B in 1..MaxVal,
    N in 0..MaxVal,
    P in 2..MaxVal,

    % the difference a - b is a prime p
    P in PrimeDomain,
    A #>= B,
    P #= A - B,
    % the product a * b is the square n^2. Propagating A * B #= N * N directly
    % is slow (every choice of a costs about half a second), so n^2 is read from
    % a table of the squares of 0..max_val, which is far cheaper.
    findall([K, KK], (between(0, MaxVal, K), KK is K * K), Squares),
    MaxProduct is MaxVal * MaxVal,
    Product in 0..MaxProduct,
    A * B #= Product,
    tuples_in([[N, Product]], Squares),
    Vars = [A, B, P, N].

% The union of the integers in the list, written as a clpfd domain.
domain_of([First|Rest], Domain) :-
    foldl([X, Acc, Acc \/ X]>>true, Rest, First, Domain).

% A number is prime when it is at least 2 and no number from 2 up to its square
% root divides it.
is_prime(N) :-
    N >= 2,
    Root is floor(sqrt(N)),
    \+ ( between(2, Root, D), N mod D =:= 0 ).

% a is tried from its smallest value up, then b; p and n follow.
labeling_options([leftmost]).

:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Production planning: choose quantities within per-product ceilings so that
% the shared production rate constraint holds, maximizing profit.
model(Instance, Xs, [x-Xs, total_profit-Profit], max(Profit)) :-
    A = Instance.a,
    C = Instance.c,
    U = Instance.u,
    B = Instance.b,
    length(A, NumProducts),
    length(Xs, NumProducts),
    max_list(U, MaxU),
    Xs ins 0..MaxU,
    maplist([X, Cap]>>(X #>= 0, X #=< Cap), Xs, U),
    % The rate constraint is sum(x[j] / a[j]) <= b.  Multiplying through by the
    % least common multiple of a clears the divisions without rounding.
    foldl(lcm_step, A, 1, LcmA),
    maplist({LcmA}/[Aj, Coefficient]>>(Coefficient is LcmA // Aj), A, Rate),
    Bound is B * LcmA,
    scalar_product(Rate, Xs, #=<, Bound),
    scalar_product(C, Xs, #=, Profit).

% Least common multiple built from gcd, which SWI-Prolog arithmetic provides.
lcm_step(Value, Accumulated, Lcm) :-
    Lcm is Accumulated * Value // gcd(Accumulated, Value).

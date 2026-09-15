:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Split A into two disjoint non-empty subsets S and T with equal sums.
model(Instance, Vars, [in_S-InS, in_T-InT]) :-
    % The field name is a bare capital, so read it with get_dict rather than
    % the functional notation.
    get_dict('A', Instance, A),
    length(A, N),
    length(InS, N),
    length(InT, N),
    InS ins 0..1,
    InT ins 0..1,
    append(InS, InT, Vars),
    scalar_product(A, InS, #=, Sum),
    scalar_product(A, InT, #=, Sum),
    % Disjointness: the reference writes sum(in_S * in_T) == 0, which is the
    % same as forbidding any element from landing in both subsets.
    maplist([S, T]>>(S + T #=< 1), InS, InT),
    sum(InS, #>, 0),
    sum(InT, #>, 0).

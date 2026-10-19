% csplib_084_hadamard_matrix: 2cc Hadamard matrix Legendre pairs.
% For every odd positive integer l, with m = (l - 1) / 2, two sequences
% A = [a_1..a_l] and B = [b_1..b_l] with domains {-1, +1}.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [a-As, b-Bs], none) :-
    memberchk(l-L, Instance),
    M is (L - 1) // 2,
    length(As, L),
    length(Bs, L),
    As :: [-1, 1],
    Bs :: [-1, 1],
    append(As, Bs, Vars),

    % m quadratic constraints: PAF(A, s) + PAF(B, s) = -2, for s = 1..m
    % PAF is the periodic autocorrelation function, indices taken mod l.
    (   for(S, 1, M), param(As, Bs, L) do
        periodic_autocorrelation(As, S, L, PA),
        periodic_autocorrelation(Bs, S, L, PB),
        PA + PB #= -2
    ),

    % linear constraint: a_1 + ... + a_l = 1
    sum(As) #= 1,
    % linear constraint: b_1 + ... + b_l = 1
    sum(Bs) #= 1.

% PAF(X, S) = sum_{i=1..L} x_i * x_{(i + S) mod L}
periodic_autocorrelation(Xs, S, L, PAF) :-
    (   for(I, 1, L), foreach(T, Ts), param(Xs, S, L) do
        J is (I - 1 + S) mod L + 1,
        nth1(I, Xs, XI),
        nth1(J, Xs, XJ),
        T #= XI * XJ
    ),
    PAF #= sum(Ts).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

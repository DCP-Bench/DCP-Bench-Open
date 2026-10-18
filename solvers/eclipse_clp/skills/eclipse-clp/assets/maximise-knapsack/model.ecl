% 0/1 knapsack, maximise the value. bb_min/3 only minimises, so the model
% minimises the negated value; the search then proves the optimum.
:- lib(ic).
:- lib(branch_and_bound).

weights([12, 7, 11, 8, 9]).
values([24, 13, 23, 15, 16]).
capacity(26).

main :-
    weights(W), values(V), capacity(Cap),
    length(W, N),
    length(X, N),
    X :: 0..1,                              % X[i] = 1 when item i is taken
    % total weight within the capacity
    ( foreach(Wi, W), foreach(Xi, X), foreach(T, Ts) do T = Wi*Xi ),
    sum(Ts) #=< Cap,
    % cost = - total value, a variable (bb_min needs a variable, not an expression)
    ( foreach(Vi, V), foreach(Xj, X), foreach(U, Us) do U = Vi*Xj ),
    Cost #= -sum(Us),
    % bb_min/3 returns the proven optimum when it exits normally
    % The default options print "Found a solution with cost ..." lines on stdout;
    % report_success and report_failure set to true/0 silence them.
    bb_min(search(X, 0, input_order, indomain_max, complete, []), Cost,
           bb_options{report_success:true/0, report_failure:true/0}),
    Profit is -Cost,
    printf("Chosen: %w%n", [X]),
    printf("Value: %d%n", [Profit]).

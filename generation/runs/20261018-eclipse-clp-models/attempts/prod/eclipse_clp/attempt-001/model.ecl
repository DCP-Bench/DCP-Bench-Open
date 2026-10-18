% Production problem: for each product j with parameters a[j], c[j] and upper
% bound u[j], choose the integer production quantity X[j] to maximise the total
% profit, the sum of c[j] * X[j] over all products.

% The constraint on the time budget: the sum of (1/a[j]) * X[j] is at most b.
% The model keeps the coefficients integer by multiplying through by
% P, the product of all a[j]. Each P/a[j] is an integer because a[j] divides P.

:- lib(ic).

model(Instance, Vars, [total_profit-Profit, x-Xs], Objective) :-
    memberchk(a-As, Instance),
    memberchk(c-Cs, Instance),
    memberchk(u-Us, Instance),
    memberchk(b-B, Instance),
    length(As, N),
    length(Xs, N),

    % X[j] is between 0 and u[j] for all j in P.
    ( foreach(X, Xs), foreach(U, Us) do
        X :: 0..U
    ),

    % Time budget: the sum of (1/a[j]) * X[j] is at most b.
    ( fromto(1, P0, P1, P), foreach(A, As) do
        P1 is P0 * A
    ),
    ( foreach(A, As), foreach(X, Xs), foreach(T, Ts), param(P) do
        Q is P // A,
        T #= Q * X
    ),
    sum(Ts) #=< P * B,

    % Total profit: the sum of c[j] * X[j] over all products.
    ( foreach(C, Cs), foreach(X, Xs), foreach(T, Profits) do
        T #= C * X
    ),
    Profit #= sum(Profits),
    Objective = max(Profit),

    Vars = Xs.

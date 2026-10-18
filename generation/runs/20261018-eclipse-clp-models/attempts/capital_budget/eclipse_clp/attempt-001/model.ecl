% Capital budget: a company considers a number of investments. Each investment
% yields a net present value (NPV) and needs a cash outflow now. The total
% outflow is limited by a budget. Choose the investments that maximise the
% total NPV. Output x: whether each investment is chosen (list of booleans),
% z: the total NPV (integer).

:- lib(ic).

model(Instance, Xs, [x-Xs, z-Z], max(Z)) :-
    memberchk(budget-Budget, Instance),
    memberchk(cash_flow-CashFlow, Instance),
    memberchk(npv-NPV, Instance),
    length(NPV, N),
    length(Xs, N),
    Xs :: 0..1,

    % The cash outflow of the chosen investments must fit in the budget.
    ( foreach(C, CashFlow), foreach(X, Xs), foreach(T, Ts) do T #= C * X ),
    sum(Ts) #=< Budget,

    % The total NPV is the sum of the NPVs of the chosen investments.
    ( foreach(P, NPV), foreach(X, Xs), foreach(Q, Qs) do Q #= P * X ),
    ( foreach(P, NPV), fromto(0, A, B, Total) do B is A + P ),
    Z :: 0..Total,
    Z #= sum(Qs).

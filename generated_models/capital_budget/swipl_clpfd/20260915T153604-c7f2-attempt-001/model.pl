:- use_module(library(clpfd)).
:- use_module(library(lists)).

% Capital budgeting: choose investments whose combined cash outflow fits the
% budget, maximizing total net present value.
model(Instance, Vars, [z-Z, x-Xs], max(Z)) :-
    Npv = Instance.npv,
    CashFlow = Instance.cash_flow,
    Budget = Instance.budget,
    length(Npv, N),
    length(Xs, N),
    Xs ins 0..1,
    sum_list(Npv, NpvTotal),
    Z in 0..NpvTotal,
    Vars = [Z|Xs],
    scalar_product(CashFlow, Xs, #=<, Budget),
    scalar_product(Npv, Xs, #=, Z).

:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Set covering: hire the cheapest crew such that every task has at least one
% qualified worker on it.
model(Instance, Vars, [total_cost-TotalCost, workers-Workers], min(TotalCost)) :-
    NbWorkers = Instance.nb_workers,
    NumTasks = Instance.num_tasks,
    % Both of these field names are capitalised, so read them with get_dict.
    get_dict('Cost', Instance, Cost),
    get_dict('Qualified', Instance, Qualified),
    length(Workers, NbWorkers),
    Workers ins 0..1,
    sum_list(Cost, CostSum),
    % The reference declares total_cost over 0..nb_workers * sum(Cost).
    Ceiling is NbWorkers * CostSum,
    TotalCost in 0..Ceiling,
    Vars = [TotalCost|Workers],
    scalar_product(Cost, Workers, #=, TotalCost),
    length(Qualified, NumTasks),
    % Qualified is ragged: one list of 1-based worker ids per task.
    maplist({Workers}/[Crew]>>staffed(Workers, Crew), Qualified).

staffed(Workers, Crew) :-
    maplist({Workers}/[Id, Hired]>>(J is Id - 1, nth0(J, Workers, Hired)),
            Crew, Hires),
    sum(Hires, #>=, 1).

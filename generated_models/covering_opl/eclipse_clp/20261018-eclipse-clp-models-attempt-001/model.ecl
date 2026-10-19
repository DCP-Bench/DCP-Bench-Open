% Covering problem (covering_opl): select a set of workers to perform all the tasks,
% minimizing the total hiring cost. Each worker can perform certain tasks and has a
% hiring cost. Output total_cost, and workers[i] = 1 if worker i is hired, 0 otherwise.

:- lib(ic).
:- lib(listut).

model(Instance, Ws, [total_cost-Total, workers-Ws], min(Total)) :-
    memberchk(nb_workers-NW, Instance),
    memberchk('Qualified'-Qual, Instance),
    memberchk('Cost'-Costs, Instance),

    % Each worker is hired or not.
    length(Ws, NW),
    Ws :: 0..1,

    % Ensure that all tasks are performed: each task needs at least one hired qualified worker.
    ( foreach(Q, Qual), param(Ws) do
        ( foreach(W, Q), foreach(V, Vs), param(Ws) do
            nth1(W, Ws, V)
        ),
        sum(Vs) #>= 1
    ),

    % Minimize the total hiring cost of the selected workers.
    ( foreach(W, Ws), foreach(C, Costs), foreach(T, Terms) do
        T #= W * C
    ),
    Total #= sum(Terms).

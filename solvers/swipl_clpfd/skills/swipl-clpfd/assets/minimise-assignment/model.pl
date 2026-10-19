% Assign each of 3 tasks to a different worker at the lowest total cost.
% Shows: a decision variable per task holding the worker, all_distinct/1,
% element/3 over a flattened cost matrix (1-based index), and minimise.
:- use_module(library(clpfd)).
:- initialization(main, main).

% cost[Task][Worker], both 1-based in the text, flattened row by row.
cost_matrix([[9, 2, 7],
             [6, 4, 3],
             [5, 8, 1]]).

main :-
    cost_matrix(Matrix),
    append(Matrix, Flat),
    length(Matrix, N),
    length(Worker, N),
    Worker ins 1..N,
    all_distinct(Worker),
    costs(Worker, 1, N, Flat, Costs),
    sum(Costs, #=, Total),
    once(labeling([min(Total)], Worker)),
    format("Workers: ~w~n", [Worker]),
    format("Total cost: ~w~n", [Total]).

% Cost of task T with worker W is the (T-1)*N + W element of the flat matrix.
costs([], _, _, _, []).
costs([W|Ws], T, N, Flat, [C|Cs]) :-
    Index #= (T - 1) * N + W,
    element(Index, Flat, C),
    T1 is T + 1,
    costs(Ws, T1, N, Flat, Cs).

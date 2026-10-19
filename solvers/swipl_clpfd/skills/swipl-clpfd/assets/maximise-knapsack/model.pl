% 0/1 knapsack: choose items to maximise the total value within a capacity.
% Shows: boolean variables as 0/1, a linear capacity constraint, and
% labeling([max(Expr)]), whose first solution is the proven optimum.
:- use_module(library(clpfd)).
:- initialization(main, main).

item(a, 3, 4).
item(b, 4, 5).
item(c, 2, 3).
item(d, 5, 8).

capacity(9).

main :-
    findall(Name, item(Name, _, _), Names),
    findall(Weight, item(_, Weight, _), Weights),
    findall(Value, item(_, _, Value), Values),
    capacity(Capacity),
    length(Names, N),
    length(Take, N),
    Take ins 0..1,
    scalar_product(Weights, Take, #=<, Capacity),
    scalar_product(Values, Take, #=, Total),
    once(labeling([max(Total)], Take)),
    findall(Name, (nth1(I, Names, Name), nth1(I, Take, 1)), Chosen),
    format("Chosen: ~w~n", [Chosen]),
    format("Best value: ~w~n", [Total]).

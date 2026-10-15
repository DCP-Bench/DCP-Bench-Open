% Count every way to pay 20 with coins of value 1, 2, 5 and 10.
% Shows: all solutions with findall/3 over labeling/2 of the decision variables,
% and a linear equality with scalar_product/4.
:- use_module(library(clpfd)).
:- initialization(main, main).

coins([1, 2, 5, 10]).

% Counts[i] is how many coins of value Values[i] are used.
payment(Target, Counts) :-
    coins(Values),
    length(Values, N),
    length(Counts, N),
    Counts ins 0..Target,
    scalar_product(Values, Counts, #=, Target).

main :-
    % Only the decision variables are labelled, so each solution is listed once.
    findall(Counts, (payment(20, Counts), labeling([], Counts)), Solutions),
    length(Solutions, Count),
    format("Ways to pay 20: ~w~n", [Count]),
    Solutions = [First|_],
    format("First: ~w~n", [First]).

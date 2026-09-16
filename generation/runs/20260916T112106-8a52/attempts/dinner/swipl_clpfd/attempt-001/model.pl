:- use_module(library(clpfd)).

% Dinner: twenty people for twenty dollars.  Prices are doubled through so the
% fifty-cent child stays an integer.
model(_Instance, Vars,
      [grandparents-Grandparents, parents-Parents, children-Children]) :-
    Vars = [Grandparents, Parents, Children],
    Grandparents in 1..6,
    Parents in 1..10,
    Children in 1..40,
    Grandparents * 6 + Parents * 4 + Children * 1 #= 20 * 2,
    Grandparents + Parents + Children #= 20.

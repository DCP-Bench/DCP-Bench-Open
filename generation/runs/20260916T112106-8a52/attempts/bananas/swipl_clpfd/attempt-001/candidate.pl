:- use_module(library(clpfd)).

% Bananas: buy exactly 100 fruits for exactly 100 dollars, taking as few
% bananas and apples as possible.  Five bananas cost three dollars, seven
% oranges five, nine mangoes seven and three apples nine; multiplying through
% by 3*5*7*9 = 945 clears the divisions, which is what the reference does.
model(_Instance, Vars,
      [bananas-Bananas, oranges-Oranges, mangoes-Mangoes, apples-Apples],
      min(TheSum)) :-
    Fruits = [Bananas, Oranges, Mangoes, Apples],
    Fruits ins 1..100,
    TheSum in 1..2000,
    Vars = [TheSum|Fruits],
    TheSum #= Bananas + Apples,
    3 * Bananas * 189 + 5 * Oranges * 135
        + 7 * Mangoes * 105 + 9 * Apples * 315 #= 100 * 945,
    sum(Fruits, #=, 100).

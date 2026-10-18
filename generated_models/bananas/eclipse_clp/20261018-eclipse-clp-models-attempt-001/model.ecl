% Bananas: buy fruits (bananas, oranges, mangoes, apples) for a fixed budget.
% Five bananas cost three dollars, seven oranges cost five dollars, nine mangoes
% cost seven dollars, and three apples cost nine dollars. Purchase 100 fruits in
% 100 dollars. All types of fruits need to be purchased, but bananas and apples
% should be of minimum quantity.

:- lib(ic).

model(_Instance, [B, O, M, A], [bananas-B, oranges-O, mangoes-M, apples-A], min(B + A)) :-
    % I need to purchase 100 fruits in total.
    % all types of fruits need to be purchased
    [B, O, M, A] #:: 1..100,
    B + O + M + A #= 100,
    % Five bananas cost three dollars, seven oranges cost five dollars, nine mangoes
    % cost seven dollars, and three apples cost nine dollars. I need to purchase
    % 100 fruits in 100 dollars. Scaled by 315 to keep the prices integral:
    % 189 bananas + 225 oranges + 245 mangoes + 945 apples = 31500.
    189*B + 225*O + 245*M + 945*A #= 31500.
    % bananas and apples should be of minimum quantity: the objective is B + A.

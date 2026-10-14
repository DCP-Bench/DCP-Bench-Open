% Bananas: buy exactly 100 fruits for exactly 100 dollars, at least one of every kind,
% with as few bananas and apples as possible (the buyer does not like them).
% Prices: 5 bananas cost 3 dollars, 7 oranges cost 5, 9 mangoes cost 7, 3 apples cost 9.
% These numbers belong to the problem statement, not to an instance (there is no instance data).

% How many of each fruit are bought: at least 1 of each (all kinds must be bought) and at most
% 100, since 100 fruits are bought in total.
quantity(1..100).
1 { bananas(Q) : quantity(Q) } 1.
1 { oranges(Q) : quantity(Q) } 1.
1 { mangoes(Q) : quantity(Q) } 1.
1 { apples(Q)  : quantity(Q) } 1.

% Exactly 100 fruits are bought.
:- not 100 = #sum { Q,b : bananas(Q); Q,o : oranges(Q); Q,m : mangoes(Q); Q,a : apples(Q) }.

% Exactly 100 dollars are spent. A fruit costs a fraction of a dollar (3/5, 5/7, 7/9, 9/3), and
% ASP has no fractions, so every price is multiplied by 3*5*7*9 = 945:
% banana 567 = 3*945/5, orange 675 = 5*945/7, mango 735 = 7*945/9, apple 2835 = 9*945/3,
% and the budget becomes 100*945 = 94500.
:- not 94500 = #sum { 567*Q,b : bananas(Q); 675*Q,o : oranges(Q);
                      735*Q,m : mangoes(Q); 2835*Q,a : apples(Q) }.

% Bananas and apples should be of minimum quantity: minimise their total.
#minimize { Q,b : bananas(Q); Q,a : apples(Q) }.

#show bananas/1.
#show oranges/1.
#show mangoes/1.
#show apples/1.

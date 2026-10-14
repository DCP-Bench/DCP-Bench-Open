% Diet problem: choose how many servings of each of four foods to eat so that the diet meets the
% minimum amount of each nutrient (calories, chocolate, sugar, fat) at the lowest total price.
% Instance facts: n(N) foods numbered 0..N-1, price(F, P): price in cents of one serving of food F,
% limits(L, R): the least amount R required of nutrient L.
food(0..N-1) :- n(N).

% The nutrient content of one serving, fixed by the problem statement (not by the instance):
% content(L, F, Q): a serving of food F holds Q of nutrient L.
% Nutrients: 0 calories, 1 chocolate (ounces), 2 sugar (ounces), 3 fat (ounces).
% Foods: 0 chocolate cake, 1 chocolate ice cream, 2 cola, 3 pineapple cheesecake.
content(0,0,400). content(0,1,200). content(0,2,150). content(0,3,500).
content(1,0,3).   content(1,1,2).   content(1,2,0).   content(1,3,0).
content(2,0,2).   content(2,1,2).   content(2,2,4).   content(2,3,4).
content(3,0,2).   content(3,1,4).   content(3,2,1).   content(3,3,5).

% The number of servings of food F is written in unary: servings(F, V) says food F is eaten
% at least V times, for V from 1 to 10000, the most the problem allows. Sums over these
% atoms are propagated much more strongly than a sum over one atom per count.
{ servings(F,V) } :- food(F), V = 1..10000.
:- servings(F,V), V > 1, not servings(F,V - 1).

% The diet holds at least the required amount of every nutrient.
:- limits(L,R), #sum { Q,F,V : servings(F,V), content(L,F,Q) } < R.

% cost(S): the total price of the diet is S, to be minimised. The problem keeps it between 0
% and 1000. The value is chosen and tied to the prices by one sum, because defining it with
% a sum assignment would ground one atom for every possible total.
1 { cost(S) : S = 0..1000 } 1.
:- #sum { P,F,V : servings(F,V), price(F,P) ; -S,total,S : cost(S) } != 0.
#minimize { S,total : cost(S) }.

% Which servings are eaten is not part of the answer, so solutions are projected onto cost.
#project cost/1.
#show cost/1.

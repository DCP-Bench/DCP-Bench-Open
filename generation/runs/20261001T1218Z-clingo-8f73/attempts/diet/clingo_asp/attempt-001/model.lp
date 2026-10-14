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

% x(F, V): V servings of food F are eaten. The problem allows between 0 and 10000 servings of each food.
1 { x(F,V) : V = 0..10000 } 1 :- food(F).

% The diet holds at least the required amount of every nutrient.
:- limits(L,R), #sum { V*Q,F : x(F,V), content(L,F,Q) } < R.

% cost: the total price of the diet, which is to be minimised. The problem keeps it
% within 0..1000.
cost(S) :- S = #sum { V*P,F : x(F,V), price(F,P) }.
:- cost(S), S > 1000.
#minimize { S : cost(S) }.

#show cost/1.

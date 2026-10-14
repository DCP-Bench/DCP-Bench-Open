% Production planning: choose how many units x[j] of each product to make, within 0..u[j], so that
% the capacity used, the sum of x[j]/a[j], stays at most b, and the total profit sum of c[j]*x[j] is largest.
% Instance facts: a(J,A): capacity divisor of product J; c(J,C): profit per unit; u(J,U): upper limit; b(B).
product(J) :- a(J,_).

% x(J,V): V units of product J are made, between 0 and u[j].
1 { x(J,V) : V = 0..U } 1 :- product(J), u(J,U).

% scale(0..n): scale(J,P) is the product of a[0..J-1]; the product of all a[j] is a common
% multiple of them, used to turn the fractions 1/a[j] into integers (clingo has no division
% that stays exact). Multiplying both sides of the capacity constraint by it does not change it.
scale(0,1).
scale(J+1,P*A) :- scale(J,P), a(J,A).
common(P) :- scale(N,P), N = #count { J : product(J) }.

% The capacity used, the sum of x[j]/a[j], must not exceed b: with the common multiple P,
% the sum of (P/a[j]) * x[j] must not exceed b * P.
:- common(P), b(B), #sum { (P/A)*V,J : x(J,V), a(J,A) } > B*P.

% total_profit is the sum of c[j]*x[j] over all products, to be maximised.
total_profit(S) :- S = #sum { C*V,J : x(J,V), c(J,C) }.
#maximize { S : total_profit(S) }.

#show x/2.
#show total_profit/1.

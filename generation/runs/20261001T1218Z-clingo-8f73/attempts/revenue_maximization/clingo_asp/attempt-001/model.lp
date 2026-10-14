% Revenue maximisation for flight packages: decide how many units of each package (a bundle of
% flight legs) to sell, no more than its demand, without selling more seats on a leg than are
% available, so that the total revenue is largest.
% Instance facts: available_seats(J,S): seats on leg J; demand(I,D): estimated demand for package I;
% revenue(I,R): revenue of one unit of package I; delta(I,J,1): package I uses leg J.
package(I) :- demand(I,_).

% Units sold use an order encoding: sold(I,V) holds when at least V units of package I are sold,
% V in 1..demand(I) (the reference allows 0..max demand and also bounds each package by its own
% demand). Unary threshold atoms keep the sums below easy to propagate.
{ sold(I,V) : V = 1..D } :- demand(I,D).
:- sold(I,V+1), not sold(I,V), V >= 1.

% packages_to_sell(I,V): exactly V units of package I are sold.
packages_to_sell(I,0) :- package(I), not sold(I,1).
packages_to_sell(I,V) :- sold(I,V), not sold(I,V+1).

% Capacity: the units sold of all packages using a leg must not exceed the seats available on it.
:- available_seats(J,S), #sum { 1,I,V : sold(I,V), delta(I,J,1) } > S.

% max_revenue is the revenue of all units sold, to be maximised.
max_revenue(Z) :- Z = #sum { R,I,V : sold(I,V), revenue(I,R) }.
#maximize { Z : max_revenue(Z) }.

#show packages_to_sell/2.
#show max_revenue/1.

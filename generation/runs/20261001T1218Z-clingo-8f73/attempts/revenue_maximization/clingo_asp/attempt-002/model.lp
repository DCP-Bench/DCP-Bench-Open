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

% The revenue to maximise is the revenue per unit times the units sold, over all packages.
#maximize { R,I,V : sold(I,V), revenue(I,R) }.

% max_revenue reports that revenue. It is added up package by package: partial(I,Z) says the
% packages 0..I-1 bring in Z. A single "Z = #sum {...}" over all packages would make the grounder
% build one large sum constraint for every possible total, which is far too slow to solve.
partial(0,0).
partial(I+1,Z+R*V) :- partial(I,Z), packages_to_sell(I,V), revenue(I,R).
max_revenue(Z) :- partial(N,Z), N = #count { I : package(I) }.

#show packages_to_sell/2.
#show max_revenue/1.

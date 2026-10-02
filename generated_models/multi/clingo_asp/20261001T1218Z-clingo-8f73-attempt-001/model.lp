% Multi-commodity transportation: several products are shipped from origins to destinations.
% Each origin has a supply of each product, each destination a demand for each product, and the
% total amount shipped on a route from one origin to one destination is limited. Ship so that the
% supplies are not exceeded, the demands are met, the limits hold and the shipping cost is smallest.
% Instance facts: supply(I, P, S): supply of product P at origin I, demand(J, P, D): demand of
% product P at destination J, limit(I, J, L): most that can be shipped from I to J in total,
% cost(I, J, P, C): cost of shipping one unit of product P from I to J.
origin(I) :- supply(I,_,_).
destination(J) :- demand(J,_,_).
product(P) :- supply(_,P,_).

% The amount shipped is written in unary: ship(I, J, P, V) says at least V units of product P are
% shipped from origin I to destination J. Sums over these atoms are propagated much more
% strongly than a sum over one atom per amount. An amount cannot exceed the supply of its
% origin or the limit of its route (the constraints below imply this; it only shortens the chains).
bound(I,J,P,B) :- supply(I,P,S), limit(I,J,L), B = #min { S ; L }.
{ ship(I,J,P,V) } :- bound(I,J,P,B), V = 1..B.
:- ship(I,J,P,V), V > 1, not ship(I,J,P,V - 1).

% Supply: the amount of product P leaving origin I does not exceed its supply.
:- supply(I,P,S), #count { J,V : ship(I,J,P,V) } > S.

% Demand: the amount of product P arriving at destination J meets its demand.
:- demand(J,P,D), #count { I,V : ship(I,J,P,V) } < D.

% Limit: the total of all products shipped from origin I to destination J stays within the limit.
:- limit(I,J,L), #count { P,V : ship(I,J,P,V) } > L.

% total_cost: the shipping cost of everything shipped, which is to be minimised. The cost is
% bounded by the total supply times the highest unit cost, as in the problem statement. It is chosen
% and tied to the shipments by one sum, because defining it with a sum assignment would ground
% one atom for every possible total.
total_supply(S) :- S = #sum { Q,I,P : supply(I,P,Q) }.
highest_cost(C) :- C = #max { U : cost(_,_,_,U) }.
max_cost(S * C) :- total_supply(S), highest_cost(C).
1 { total_cost(T) : max_cost(M), T = 0..M } 1.
:- #sum { C,I,J,P,V : ship(I,J,P,V), cost(I,J,P,C) ; -T,total,T : total_cost(T) } != 0.
#minimize { C,I,J,P,V : ship(I,J,P,V), cost(I,J,P,C) }.

% The shipments are not part of the answer, so solutions are projected onto total_cost.
#project total_cost/1.
#show total_cost/1.

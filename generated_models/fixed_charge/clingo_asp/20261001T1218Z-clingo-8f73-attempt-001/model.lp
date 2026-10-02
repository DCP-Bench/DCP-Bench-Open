% Fixed charge production: a company makes shirts, shorts and pants. Each product uses labor and
% cloth, of which the company has a limited capacity, and can be made only on a rented machine.
% Choose which machines to rent and how many of each product to make so that the profit, after
% paying the rent, is as large as possible.
% Instance facts: num_products(P), num_machines(M), renting_cost(M, C): rent of machine M,
% capacity(R, C): available amount of resource R (labor, cloth), max_production(Q),
% product(P, 0, Profit) and product(P, 1, Machine): profit of product P and the machine it needs,
% use(P, R, U): amount of resource R one unit of product P uses.
prod(0..P-1) :- num_products(P).
machine(0..M-1) :- num_machines(M).
resource(R) :- capacity(R,_).

% rent(M): machine M is rented.
{ rent(M) : machine(M) }.

% made(P, V): at least V units of product P are made, for V up to the production limit. The
% number made is written in unary, so that the sums below are propagated tightly.
{ made(P,V) } :- prod(P), max_production(Q), V = 1..Q.
:- made(P,V), V > 1, not made(P,V - 1).

% The resources used by all products stay within the capacity of each resource.
:- resource(R), capacity(R,C), #sum { U,P,V : made(P,V), use(P,R,U) } > C.

% A product can be made only if the machine it needs is rented.
:- made(P,1), product(P,1,M), not rent(M).

% z: the profit of the products made minus the rent of the machines rented, to be maximised.
% The problem declares z between 0 and 10000. The value is chosen and tied to the profit and
% rent by one sum, because defining it with a sum assignment would ground one atom for every
% possible total. The tags p, r and z keep the three kinds of terms apart in the sum.
1 { z(Z) : Z = 0..10000 } 1.
:- #sum { Profit,p,P,V : made(P,V), product(P,0,Profit) ;
          -C,r,M : rent(M), renting_cost(M,C) ;
          -Z,z,Z : z(Z) } != 0.
#maximize { Z,z : z(Z) }.

% The production plan and the rented machines are not part of the answer, so solutions are
% projected onto z.
#project z/1.
#show z/1.

% Project assignment: decide how many hours each person works on each project so that every
% person's hours add up to their supply, every project receives exactly its demand, no person
% gives a project more than their limit for it, and the total cost per hour worked is smallest.
% Instance facts: supply(I,S): person I has S hours; demand(J,D): project J needs D hours;
% cost(I,J,K): K per hour of person I on project J; limit(I,J,L): person I gives project J at most L hours.
person(I) :- supply(I,_).
project(J) :- demand(J,_).

% assign(I,J,H): person I works H hours on project J. The reference declares the hours of each
% pair as an integer in 0..10 (a bound of the problem, not of the instance), and the pair limit tightens it.
1 { assign(I,J,H) : H = 0..10, limit(I,J,L), H <= L } 1 :- person(I), project(J).

% The hours a person gives to all projects equal their supply.
:- supply(I,S), #sum { H,J : assign(I,J,H) } != S.

% The hours a project receives from all people equal its demand.
:- demand(J,D), #sum { H,I : assign(I,J,H) } != D.

% total_cost is the cost of all hours worked, to be minimised.
total_cost(C) :- C = #sum { H*K,I,J : assign(I,J,H), cost(I,J,K) }.
#minimize { C : total_cost(C) }.

#show assign/3.
#show total_cost/1.

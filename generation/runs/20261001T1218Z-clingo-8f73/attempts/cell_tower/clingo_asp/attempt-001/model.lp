% Cell towers: choose the sites on which to build towers, within a budget, so that the
% population living in regions covered by at least one tower is as large as possible.
% Instance facts: delta(I, J, B): B is 1 when a tower at site I covers region J; cost(I, C):
% building at site I costs C; population(J, P): region J has P inhabitants; budget(B).
site(I) :- cost(I,_).

% build_tower(I, true/false): whether a tower is built at site I.
{ built(I) } :- site(I).
build_tower(I,true) :- built(I).
build_tower(I,false) :- site(I), not built(I).

% The total cost of the towers built must not exceed the budget.
:- budget(B), #sum { C,I : built(I), cost(I,C) } > B.

% A region is covered when a tower is built at a site that covers it.
covered(J) :- built(I), delta(I,J,1).

% The population covered, which is to be maximised.
total_population_covered(T) :- T = #sum { P,J : covered(J), population(J,P) }.
#maximize { T : total_population_covered(T) }.

#show build_tower/2.
#show total_population_covered/1.

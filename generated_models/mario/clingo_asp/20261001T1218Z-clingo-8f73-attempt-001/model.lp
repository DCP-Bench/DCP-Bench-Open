% Mario's gold collection: Mario starts at his house, visits some houses and ends at Luigi's house,
% collecting the gold in every house he visits, without using more fuel than he has. Plan the route
% that collects the most gold.
% Instance facts: nHouses(N), marioHouse(M), luigiHouse(L), fuelLimit(F),
% arc_fuel(I, J, C): going from house I to house J burns C fuel, goldInHouse(I, G): gold in house I.
house(0..N-1) :- nHouses(N).

% s(I, J): the house following house I is J; J = I when house I is not on the route. Every
% house has one successor and is the successor of one house, so s is a permutation.
1 { s(I,J) : house(J) } 1 :- house(I).
1 { s(I,J) : house(I) } 1 :- house(J).

% For Luigi's house the successor is Mario's house: the route is closed there.
:- luigiHouse(L), marioHouse(M), not s(L,M).

% on_route(I): house I is visited. The route starts at Mario's house and follows the
% successors until Luigi's house, whose successor (Mario's house) does not extend it.
% Every house with a successor other than itself has to be on this route, which forbids
% separate loops among the other houses.
on_route(M) :- marioHouse(M).
on_route(J) :- on_route(I), s(I,J), luigiHouse(L), I != L.
:- s(I,J), I != J, not on_route(I).

% The fuel burned over all the arcs used stays within the fuel limit.
:- fuelLimit(F), #sum { C,I : s(I,J), arc_fuel(I,J,C) } > F.

% Maximise the gold in the houses visited (the houses that are not their own successor).
#maximize { G,I : s(I,J), J != I, goldInHouse(I,G) }.

#show s/2.

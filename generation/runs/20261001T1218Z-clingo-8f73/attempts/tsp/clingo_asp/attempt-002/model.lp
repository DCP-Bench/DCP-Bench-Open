% Travelling salesman: find the shortest route that visits every city exactly once and returns to
% the start; report its length. The distance between two cities is the Euclidean distance
% between their points rounded to the nearest integer.
% Instance facts: locations(I,0,X) and locations(I,1,Y): coordinates of city I. At least two cities.
city(I) :- locations(I,0,_).

% dist(I,J,D): the rounded Euclidean distance from city I to city J is D. The square root is
% not available in clingo, so D is found by squares: D rounds the root of Q exactly when
% D*(D-1) < Q <= D*(D+1) (for D >= 1); D is 0 only for identical points. The root lies
% between half of (|dx|+|dy|) and |dx|+|dy|, which bounds the values tried for D.
offset(I,J,|X1-X2|+|Y1-Y2|,(X1-X2)**2+(Y1-Y2)**2) :-
    locations(I,0,X1), locations(I,1,Y1), locations(J,0,X2), locations(J,1,Y2), I != J.
dist(I,J,0) :- offset(I,J,_,0).
dist(I,J,D) :- offset(I,J,S,Q), Q > 0, D = S/2..S, D >= 1, D*(D-1) < Q, Q <= D*(D+1).

% successor(I,J): city J is visited immediately after city I. Every city has exactly one
% successor and exactly one predecessor.
1 { successor(I,J) : city(J), J != I } 1 :- city(I).
1 { successor(I,J) : city(I), I != J } 1 :- city(J).

% The successors form one single circuit through all cities, not several separate loops: starting
% from city 0 and following successors must reach every city.
reached(0).
reached(J) :- reached(I), successor(I,J).
:- city(J), not reached(J).

% The route length is to be minimised: the sum of the distances of the legs travelled.
#minimize { D,I,J : successor(I,J), dist(I,J,D) }.

% leg(I,D): the leg leaving city I is D long.
leg(I,D) :- successor(I,J), dist(I,J,D).

% travel_distance reports the route length, the sum of all legs. It is added up city by city:
% total(I,C) says that the legs leaving cities 0..I-1 add up to C. A single "#sum" assignment would
% make the grounder build one large sum constraint for every possible length, and following the route
% instead of the city numbers would let the grounder follow loops without end.
total(0,0).
total(I+1,C+D) :- total(I,C), leg(I,D).
travel_distance(C) :- total(N,C), N = #count { I : city(I) }.

% Only the length is an output, but many routes can have the same length: project the enumeration
% onto it so that the answers are told apart by length alone.
#project travel_distance/1.

#show travel_distance/1.

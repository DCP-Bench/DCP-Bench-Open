% Aircraft assignment: choose how many aircraft of each type fly each route so
% every route's passenger demand is met, no type is used beyond its fleet, and
% the total operating cost is minimal.
% availability(I, N): N aircraft of type I; demand(J, D): passengers on route J;
% capabilities(I, J, C): passengers type I carries on route J; costs(I, J, C): its cost.
type(I) :- availability(I,_).
route(J) :- demand(J,_).
most(M) :- M = #max { N : availability(_,N) }.

% allocation(I, J, N): N aircraft of type I fly route J.
1 { allocation(I,J,N) : N = 0..M } 1 :- type(I), route(J), most(M).

% A type cannot be assigned more aircraft than are available.
:- availability(I,A), A < #sum { N,J : allocation(I,J,N) }.

% The aircraft on each route together carry at least the route's demand.
:- demand(J,D), D > #sum { C * N,I : allocation(I,J,N), capabilities(I,J,C) }.

% Minimise the total operating cost.
#minimize { C * N,I,J : allocation(I,J,N), costs(I,J,C) }.

#show allocation/3.

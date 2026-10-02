% Progressive party: some boats are designated hosts and stay put; every other boat's crew
% visits one host in each period. Boats hold a limited number of people, a guest crew visits
% each host at most once, and two crews may meet at most once. Minimise the number of hosts.
% Instance facts: n_boats(N), n_periods(T); capacity(B, C): boat B holds at most C people;
% crew_size(B, S): the crew of boat B has S people. Boats and periods are numbered from 0.
boat(0..N-1) :- n_boats(N).
period(0..T-1) :- n_periods(T).

% host(B): boat B is a host. is_host(B, true/false) reports it for every boat.
{ host(B) } :- boat(B).
is_host(B,true) :- host(B).
is_host(B,false) :- boat(B), not host(B).

% visits(P, B, V): in period P the crew of boat B is on boat V. Every crew is on exactly one boat.
1 { visits(P,B,V) : boat(V) } 1 :- period(P), boat(B).

% The crew of a host boat stays on board in every period.
:- host(B), period(P), not visits(P,B,B).

% Non-host boats cannot be visited (and a non-host crew is never on its own boat).
:- not host(V), visits(_,_,V).

% The number of people aboard a boat, host crew and guest crews together, never exceeds its
% capacity in any period.
:- capacity(V,C), period(P), C < #sum { S,B : visits(P,B,V), crew_size(B,S) }.

% A guest crew cannot visit the same boat twice.
:- not host(B), visits(P1,B,V), visits(P2,B,V), P1 < P2.

% Two crews cannot meet more than once: in at most one period are they on the same boat.
:- boat(B1), boat(B2), B1 < B2, 2 { P : visits(P,B1,V), visits(P,B2,V) }.

% The organiser wants as few host boats as possible.
#minimize { 1,B : host(B) }.

#show is_host/2.
#show visits/3.

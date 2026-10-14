% SONET ring design: place nodes on rings by installing an add-drop multiplexer (ADM) for each
% node on each ring it uses, so that every pair of nodes with traffic shares a ring, no ring
% holds more nodes than its capacity, and the total number of ADMs is as small as possible.
% Instance facts: r(R) rings, n(N) nodes, demand(I, J, D): traffic between nodes I and J,
% capacity_nodes(K, C): the most nodes ring K can host.
ring(0..R-1) :- r(R).
node(0..N-1) :- n(N).

% on_ring(K, I): node I is on ring K (one ADM).
{ on_ring(K,I) : node(I) } :- ring(K).

% Nodes with traffic between them must be on at least one common ring (each pair is
% looked at once, in the order I < J, as the problem does).
:- demand(I,J,D), I < J, D > 0, #count { K : on_ring(K,I), on_ring(K,J) } < 1.

% A ring hosts at most as many nodes as its capacity.
:- ring(K), capacity_nodes(K,C), #count { I : on_ring(K,I) } > C.

% total_adms: one ADM for every node-on-ring assignment, to be minimised.
total_adms(S) :- S = #count { K,I : on_ring(K,I) }.
#minimize { S : total_adms(S) }.

% ring_config(K, I, true/false): whether node I is on ring K.
ring_config(K,I,true) :- on_ring(K,I).
ring_config(K,I,false) :- ring(K), node(I), not on_ring(K,I).

#show ring_config/3.
#show total_adms/1.

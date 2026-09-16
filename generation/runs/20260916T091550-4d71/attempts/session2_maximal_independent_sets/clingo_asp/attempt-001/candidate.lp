% Maximal independent set: no edge has both ends selected, and no node could be
% added without breaking that.
node(0..N-1) :- n(N).

% The adjacency list is 1-based, so subtract one to reach the node index.
edge(I,J) :- adjacency_list(I,_,Neighbour), J = Neighbour - 1.

{ nodes(I,1) } :- node(I).
nodes(I,0) :- node(I), not nodes(I,1).

% Independence.
:- edge(I,J), I < J, nodes(I,1), nodes(J,1).

% Maximality: an unselected node must have a selected neighbour.
covered(I) :- edge(I,J), nodes(J,1).
:- node(I), nodes(I,0), not covered(I).

#show nodes/2.

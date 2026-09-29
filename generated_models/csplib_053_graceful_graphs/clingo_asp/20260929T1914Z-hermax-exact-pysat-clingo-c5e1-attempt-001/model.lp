% Graceful graph: label the nodes of a graph with m edges with distinct numbers
% from 0..m so that the differences across the edges are all distinct.
% graph(E, 0, U) and graph(E, 1, V) are the end nodes of edge E; m(M) is the number of
% edges and n(N) the number of nodes.

% nodes(V, L): node V has label L, from 0..m; all node labels are different.
1 { nodes(V,L) : L = 0..M } 1 :- n(N), m(M), V = 0..N-1.
:- nodes(V1,L), nodes(V2,L), V1 < V2.

% edges(E, L): edge E has label L, from 1..m; all edge labels are different.
1 { edges(E,L) : L = 1..M } 1 :- m(M), E = 0..M-1.
:- edges(E1,L), edges(E2,L), E1 < E2.

% Each edge is labelled with the absolute difference of the labels of its ends.
:- graph(E,0,U), graph(E,1,V), nodes(U,A), nodes(V,B), edges(E,L), L != |A - B|.

#show nodes/2.
#show edges/2.

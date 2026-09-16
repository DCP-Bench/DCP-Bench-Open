% Maximum clique: pick as many vertices as possible, no two of them
% non-adjacent.
vertex(0..N-1) :- n(N).

{ c(I,1) } :- vertex(I).
c(I,0) :- vertex(I), not c(I,1).

% Two vertices with no edge between them cannot both be in the clique.
:- vertex(I), vertex(J), I < J, adj(I,J,0), c(I,1), c(J,1).

#maximize { 1,I : c(I,1) }.
#show c/2.

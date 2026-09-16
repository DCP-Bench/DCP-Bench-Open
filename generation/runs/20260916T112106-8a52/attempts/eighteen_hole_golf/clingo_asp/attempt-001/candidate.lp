% Eighteen hole golf: eighteen holes of length three, four or five that add up
% to a par of seventy-two.
hole(0..17).
length(3..5).

1 { holes(I,L) : length(L) } 1 :- hole(I).

par(P) :- P = #sum { L,I : holes(I,L) }.
:- par(P), P != 72.

#show holes/2.

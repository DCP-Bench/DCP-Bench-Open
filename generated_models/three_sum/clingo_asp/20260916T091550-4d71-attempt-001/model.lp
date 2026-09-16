% Three sum: pick exactly m of the numbers so that they add up to zero.
index(I) :- nums(I,_).

{ indices(I,1) } :- index(I).
indices(I,0) :- index(I), not indices(I,1).

total(T) :- T = #sum { V,I : indices(I,1), nums(I,V) }.
:- total(T), T != 0.

picked(K) :- K = #count { I : indices(I,1) }.
:- picked(K), m(M), K != M.

#show indices/2.

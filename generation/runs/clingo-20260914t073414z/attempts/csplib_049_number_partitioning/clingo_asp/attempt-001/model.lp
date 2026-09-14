val(1..N) :- n(N).
half(H) :- n(N), H = N / 2.

% Split 1..n into two equal halves.
{ first(V) : val(V) } == H :- half(H).
second(V) :- val(V), not first(V).

% Equal sums, and equal sums of squares.
:- #sum { V : first(V) } != #sum { V : second(V) }.
:- #sum { S,V : first(V), S = V * V } != #sum { S,V : second(V), S = V * V }.

% Rank each side ascending to fill the declared 0-based lists.
a(R,V) :- first(V), R = #count { W : first(W), W < V }.
b(R,V) :- second(V), R = #count { W : second(W), W < V }.

#show a/2.
#show b/2.

val(1..N) :- n(N).
half(H) :- n(N), H = N / 2.

% Split 1..n into two equal halves.
H { first(V) : val(V) } H :- half(H).
second(V) :- val(V), not first(V).

% Equal sums, and equal sums of squares. Each aggregate is bound to a variable
% first: clingo cannot compare two aggregates directly.
suma(S) :- S = #sum { V : first(V) }.
sumb(S) :- S = #sum { V : second(V) }.
:- suma(A), sumb(B), A != B.

squarea(S) :- S = #sum { Q,V : first(V), Q = V * V }.
squareb(S) :- S = #sum { Q,V : second(V), Q = V * V }.
:- squarea(A), squareb(B), A != B.

% Rank each side ascending to fill the declared 0-based lists.
a(R,V) :- first(V), R = #count { W : first(W), W < V }.
b(R,V) :- second(V), R = #count { W : second(W), W < V }.

#show a/2.
#show b/2.

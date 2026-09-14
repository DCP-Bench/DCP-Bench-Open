pos(0..N-1) :- n(N).
val(0..N-1) :- n(N).

% One value per position.
1 { x(I,V) : val(V) } 1 :- pos(I).

% Magic sequence: the value at position I is how often I occurs in the sequence.
:- x(I,V), #count { J : x(J,I) } != V.

#show x/2.

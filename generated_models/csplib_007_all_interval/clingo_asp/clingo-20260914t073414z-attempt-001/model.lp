pos(0..N-1) :- n(N).
pitch(0..N-1) :- n(N).

% A permutation of the pitch classes.
1 { x(I,V) : pitch(V) } 1 :- pos(I).
:- x(I1,V), x(I2,V), I1 < I2.

% Successive absolute differences, themselves all different.
diffs(I,D) :- x(I,A), x(I+1,B), D = |A - B|.
:- diffs(I1,D), diffs(I2,D), I1 < I2.

#show x/2.
#show diffs/2.

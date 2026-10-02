% Climbing stairs: climb a stair of n steps by taking between m1 and m2 steps at a time. The list
% of n moves records the steps taken at each move, with 0 for the moves left over after the top is reached.
% Instance facts: n(N): steps in the stair; m1(A), m2(B): fewest and most steps taken in one move.
move(0..N-1) :- n(N).

% steps(I,V): move I takes V steps. In the worst case every move is one step, so there are n moves,
% and each takes either no step or between m1 and m2 steps.
1 { steps(I,V) : V = 0 ; steps(I,V) : V = A..B } 1 :- move(I), m1(A), m2(B).

% The steps of all moves add up to the number of steps of the stair.
:- n(N), #sum { V,I : steps(I,V) } != N.

% Trailing zeros: once a move takes no step, every later move takes none either. It is enough
% to forbid a move that takes steps right after a move that took none.
:- steps(I,V), V > 0, steps(I-1,0).

#show steps/2.

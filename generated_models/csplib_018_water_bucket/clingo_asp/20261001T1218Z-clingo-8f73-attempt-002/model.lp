% Water bucket (CSPLib 18): buckets of given capacities hold water. A move pours one bucket into
% another until the source is empty or the target is full. Reach the goal state with as few
% moves as possible.
% Instance: capacities(B, C), initial_state(B, A) and goal_state(B, A) give, for bucket B, its
% capacity, its starting amount and its goal amount. The output is a sequence of exactly
% MAX_STEPS states, which the predicate mAX_STEPS(M) carries (the runner lowers only the first
% letter of the field name), followed by padding states once the goal is reached: pADDING_VALUE(P)
% is the padding value.

bucket(B) :- capacities(B,_).
step(0..M-1) :- mAX_STEPS(M).

% amount(B, A): bucket B can hold A pints, from 0 up to its capacity. The next-state rules below
% only create states inside this range. Without it the grounder, which pairs atoms without
% knowing which belong to the same state, derives ever larger and negative amounts at every step
% and the grounding grows out of memory.
amount(B,0..C) :- capacities(B,C).

% state(T, B, A): the T-th state of the sequence has A pints in bucket B. The sequence starts
% with the initial state and a state exists only until the goal has been reached.
state(0,B,A) :- initial_state(B,A).
active(T) :- state(T,_,_).

% The goal has been reached in state T when every bucket holds its goal amount.
off_goal(T) :- active(T), goal_state(B,A), not state(T,B,A).
at_goal(T) :- active(T), not off_goal(T).

% pour_option(T, I, J, Q): in state T bucket I can be poured into bucket J, moving Q pints: the
% source must hold water, the target must have room, and the amount moved is the smaller of the
% water in the source and the room in the target.
pour_option(T,I,J,Q) :- active(T), not at_goal(T), step(T+1), state(T,I,X), state(T,J,Y),
                        capacities(J,C), I != J, X > 0, Y < C, Q = #min { X; C - Y }.

% Every state that is not the goal is followed by exactly one pour. When the last state of the
% sequence is not the goal, no pour is possible there, so the goal must be reached in time.
1 { pour(T,I,J,Q) : pour_option(T,I,J,Q) } 1 :- active(T), not at_goal(T).

% The next state: the source loses Q pints, the target gains Q pints, the others are unchanged.
state(T+1,I,X-Q) :- pour(T,I,J,Q), state(T,I,X), amount(I,X-Q).
state(T+1,J,Y+Q) :- pour(T,I,J,Q), state(T,J,Y), amount(J,Y+Q).
state(T+1,B,A)   :- pour(T,I,J,Q), state(T,B,A), B != I, B != J.

% The sequence lists the states and, after the goal, the padding state in every remaining step.
sequence(T,B,A) :- state(T,B,A).
sequence(T,B,P) :- step(T), not active(T), bucket(B), pADDING_VALUE(P).

% The cost is the number of pours, one less than the number of states before the padding.
cost(C) :- C = #count { T : active(T), T > 0 }.
#minimize { 1,T : active(T), T > 0 }.

#show cost/1.
#show sequence/3.

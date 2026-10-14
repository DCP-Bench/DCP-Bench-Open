% Archery puzzle: an archer shoots any number of arrows at targets with given point values and
% wants her total score to come as close as possible to a target score (above or below it).
% Instance facts: targets(I, V): hitting target I scores V points; target_score(T): the score
% she aims for. hits(I, H) says target I is hit H times.
target(I) :- targets(I,_).
last_target(N - 1) :- N = #count { I : target(I) }.

% Each target is hit between 0 and target_score times (the bound used by the problem), and no
% target is hit so often that its points alone pass twice the target score (the bound the problem
% puts on the total score, and all points are positive).
1 { hits(I,H) : H = 0..T, H * V <= 2 * T } 1 :- targets(I,V), target_score(T).

% subtotal(I, S): the targets 0..I together score S points. A running total, built one target at
% a time, lets the solver see the sum as a chain of small steps; a single sum over all targets
% does not propagate well when hits range over 0..target_score. Totals past twice the target score
% are left out: the problem does not allow them.
subtotal(0,H * V) :- hits(0,H), targets(0,V).
subtotal(I,S + H * V) :- subtotal(I - 1,S), hits(I,H), targets(I,V), target_score(T),
                         S + H * V <= 2 * T.

% The score is the total over all targets.
score(S) :- last_target(I), subtotal(I,S).

% Every combination of hits must end in a score: a combination whose running total passes twice
% the target score at some point has no score and is not a valid answer.
:- not score(_).

% The deviation is the distance between the score and the target score.
deviation(|T - S|) :- score(S), target_score(T).

% The archer wants the score as close as possible to the target score.
#minimize { D : deviation(D) }.

#show hits/2.

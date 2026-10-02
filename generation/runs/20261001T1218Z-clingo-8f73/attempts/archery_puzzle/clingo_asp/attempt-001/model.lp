% Archery puzzle: an archer shoots any number of arrows at targets with given point values and
% wants her total score to come as close as possible to a target score (above or below it).
% Instance facts: targets(I, V): hitting target I scores V points; target_score(T): the score
% she aims for. hits(I, H) says target I is hit H times.
target(I) :- targets(I,_).

% Each target is hit between 0 and target_score times (the bound used by the problem).
1 { hits(I,0..T) } 1 :- target(I), target_score(T).

% The score is the sum over all targets of the number of hits times its points. It never
% exceeds twice the target score, the bound used by the problem.
score(S) :- S = #sum { H * V,I : hits(I,H), targets(I,V) }.
:- score(S), target_score(T), S > 2 * T.

% The deviation is the distance between the score and the target score.
deviation(|T - S|) :- score(S), target_score(T).

% The archer wants the score as close as possible to the target score.
#minimize { D : deviation(D) }.

#show hits/2.

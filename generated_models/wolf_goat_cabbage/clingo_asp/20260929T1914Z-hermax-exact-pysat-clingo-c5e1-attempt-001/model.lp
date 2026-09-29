% Wolf, goat and cabbage: a farmer ferries a wolf, a goat and a cabbage across
% a river in a boat that carries the farmer and at most one item. The wolf must
% never be left alone with the goat, nor the goat with the cabbage. The answer
% lists, for each stage, which shore (0 = start, 1 = destination) each item and
% the boat are on.
steps(0..S-1) :- stage(S).

% Each item and the boat is on one of the two shores at every stage.
1 { wolf_pos(I,P) : P = 0..1 } 1 :- steps(I).
1 { goat_pos(I,P) : P = 0..1 } 1 :- steps(I).
1 { cabbage_pos(I,P) : P = 0..1 } 1 :- steps(I).
1 { boat_pos(I,P) : P = 0..1 } 1 :- steps(I).

% Everything starts on the first shore ...
:- wolf_pos(0,1).
:- goat_pos(0,1).
:- cabbage_pos(0,1).
:- boat_pos(0,1).
% ... and ends on the far shore.
:- stage(S), wolf_pos(S-1,0).
:- stage(S), goat_pos(S-1,0).
:- stage(S), cabbage_pos(S-1,0).
:- stage(S), boat_pos(S-1,0).

% The boat crosses the river at every stage.
:- steps(I), steps(I-1), boat_pos(I,P), boat_pos(I-1,P).

% The wolf and the goat are never alone together: if they share a shore the boat is there too.
:- steps(I), wolf_pos(I,P), goat_pos(I,P), boat_pos(I,B), B != P.
% The goat and the cabbage are never alone together.
:- steps(I), goat_pos(I,P), cabbage_pos(I,P), boat_pos(I,B), B != P.

% At most one of the wolf, goat and cabbage changes shore between two stages.
moved(I,wolf) :- steps(I), steps(I+1), wolf_pos(I,A), wolf_pos(I+1,B), A != B.
moved(I,goat) :- steps(I), steps(I+1), goat_pos(I,A), goat_pos(I+1,B), A != B.
moved(I,cabbage) :- steps(I), steps(I+1), cabbage_pos(I,A), cabbage_pos(I+1,B), A != B.
:- steps(I), #count { X : moved(I,X) } > 1.

#show wolf_pos/2.
#show goat_pos/2.
#show cabbage_pos/2.
#show boat_pos/2.

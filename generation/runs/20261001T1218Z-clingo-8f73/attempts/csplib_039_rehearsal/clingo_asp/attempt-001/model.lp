% Rehearsal problem: order the pieces of a concert for rehearsal so that the total time players
% spend present but not playing is as small as possible. A player arrives just before the first
% piece they play in and leaves just after the last one.
% Instance facts: num_pieces(N), num_players(M), duration(P, D): length of piece P,
% rehearsal(Q, P, V): V is 1 when player Q plays in piece P, and 0 otherwise.
slot(0..N-1) :- num_pieces(N).
piece(0..N-1) :- num_pieces(N).
player(0..M-1) :- num_players(M).

% rehearsal_order(I, P): piece P is rehearsed in slot I. Each slot gets one piece and
% each piece is rehearsed exactly once, so the order is a permutation.
1 { rehearsal_order(I,P) : piece(P) } 1 :- slot(I).
:- piece(P), #count { I : rehearsal_order(I,P) } != 1.

% plays(Q, I): player Q plays in the piece rehearsed in slot I.
plays(Q,I) :- rehearsal_order(I,P), rehearsal(Q,P,1).

% A player is present in every slot from the first slot they play in to the last one
% (arriving earlier or leaving later would only add waiting time, so the cheapest
% presence is the one the objective counts).
present(Q,I) :- plays(Q,J), plays(Q,K), J <= I, I <= K, slot(I).

% A player waits in a slot where they are present but not playing, for as long as the
% piece rehearsed in that slot lasts.
waiting(Q,I) :- present(Q,I), not plays(Q,I).

% Minimise the total waiting time of all players.
#minimize { D,Q,I : waiting(Q,I), rehearsal_order(I,P), duration(P,D) }.

#show rehearsal_order/2.

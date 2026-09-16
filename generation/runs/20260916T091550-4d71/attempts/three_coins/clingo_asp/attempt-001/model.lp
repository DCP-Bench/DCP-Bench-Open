% Three coins: flip exactly one coin per move and finish with every coin
% showing the same face.
coin(J) :- init(J,_).
coins(N) :- N = #count { J : coin(J) }.
move(0..K) :- num_moves(K).

{ steps(M,J,1) } :- move(M), coin(J).
steps(M,J,0) :- move(M), coin(J), not steps(M,J,1).

% The first row is the starting configuration.
:- init(J,V), steps(0,J,W), V != W.

% Exactly one coin differs between consecutive rows.
differs(M,J) :- move(M), M > 0, coin(J), steps(M,J,A), steps(M-1,J,B), A != B.
changed(M,K) :- move(M), M > 0, K = #count { J : differs(M,J) }.
:- changed(M,K), K != 1.

% The final row is all heads or all tails.
final(S) :- num_moves(K), S = #count { J : steps(K,J,1) }.
:- final(S), coins(N), S != 0, S != N.

#show steps/3.

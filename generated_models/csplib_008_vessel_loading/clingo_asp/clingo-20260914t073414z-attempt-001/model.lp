cont(0..K-1) :- n_containers(K).
xcoord(0..W) :- deck_width(W).
ycoord(0..L) :- deck_length(L).

1 { left(I,X)   : xcoord(X) } 1 :- cont(I).
1 { right(I,X)  : xcoord(X) } 1 :- cont(I).
1 { bottom(I,Y) : ycoord(Y) } 1 :- cont(I).
1 { top(I,Y)    : ycoord(Y) } 1 :- cont(I).

% Each container sits in one of its two orientations.
oriented(I) :- left(I,L), right(I,R), bottom(I,B), top(I,T),
               width(I,W), length(I,H), R - L == W, T - B == H.
oriented(I) :- left(I,L), right(I,R), bottom(I,B), top(I,T),
               width(I,W), length(I,H), R - L == H, T - B == W.
:- cont(I), not oriented(I).

% Separation required between the classes of each pair.
gap(I,J,S) :- cont(I), cont(J), I < J, classes(I,Ci), classes(J,Cj),
              separation(Ci-1,Cj-1,S).
apart(I,J) :- gap(I,J,S), right(I,R), left(J,L), R + S <= L.
apart(I,J) :- gap(I,J,S), left(I,L), right(J,R), L >= R + S.
apart(I,J) :- gap(I,J,S), top(I,T), bottom(J,B), T + S <= B.
apart(I,J) :- gap(I,J,S), bottom(I,B), top(J,T), B >= T + S.
:- cont(I), cont(J), I < J, not apart(I,J).

#show left/2.
#show right/2.
#show top/2.
#show bottom/2.

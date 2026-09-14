idx(0..N-1) :- n(N).
box(1..C) :- c(C).

% One box per ball.
1 { balls(I,X) : box(X) } 1 :- idx(I).

% No box holds a triple a + b = d. Balls are 1-based, the output is 0-based,
% so ball a is index I = a - 1 and the identity becomes K = I + J + 1.
:- balls(I,B), balls(J,B), balls(K,B), idx(I), idx(J), idx(K), I <= J, K = I + J + 1.

#show balls/2.

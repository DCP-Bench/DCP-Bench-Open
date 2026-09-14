val(0..N) :- n(N).
1 { xv(X) : val(X) } 1.
1 { yv(Y) : val(Y) } 1.

% The tiny reference is an equality when not optimizing and a lower bound when it is.
:- xv(X), yv(Y), n(N), optimize(false), X + Y != N.
:- xv(X), yv(Y), n(N), optimize(true), X + Y < N.

x(X) :- xv(X).
y(Y) :- yv(Y).

#minimize { X + Y : xv(X), yv(Y), optimize(true) }.

#show x/1.
#show y/1.

% SEND + MORE = MONEY: give each letter a different digit, with no leading zero
% in SEND, MORE or MONEY, so that the addition is correct.
% The puzzle is fixed by the problem; the instance carries no data.
letter(s;e;n;d;m;o;r;y).

% Every letter stands for exactly one digit, and no digit is used twice.
1 { digit(L,V) : V = 0..9 } 1 :- letter(L).
:- digit(L1,V), digit(L2,V), L1 < L2.

% No word starts with zero: SEND starts with S, MORE and MONEY with M.
:- digit(s,0).
:- digit(m,0).

% SEND + MORE = MONEY, each word read as a number.
:- digit(s,S), digit(e,E), digit(n,N), digit(d,D), digit(m,M), digit(o,O), digit(r,R), digit(y,Y),
   1000*S + 100*E + 10*N + D + 1000*M + 100*O + 10*R + E
   != 10000*M + 1000*O + 100*N + 10*E + Y.

% The answer: one atom per letter, s(V), e(V), ...
s(V) :- digit(s,V).
e(V) :- digit(e,V).
n(V) :- digit(n,V).
d(V) :- digit(d,V).
m(V) :- digit(m,V).
o(V) :- digit(o,V).
r(V) :- digit(r,V).
y(V) :- digit(y,V).
#show s/1.
#show e/1.
#show n/1.
#show d/1.
#show m/1.
#show o/1.
#show r/1.
#show y/1.

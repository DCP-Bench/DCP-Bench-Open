% Fractions puzzle: find nine different non-zero digits A..I such that
% A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.
% The puzzle has no data.
letter(a;b;c;d;e;f;g;h;i).

% Every letter is one digit from 1 to 9, and no digit is used twice.
1 { digit(L,V) : V = 1..9 } 1 :- letter(L).
:- digit(L1,V), digit(L2,V), L1 < L2.

% Multiplying the equation A/BC + D/EF + G/HI = 1 through by the three
% denominators D1 = BC, D2 = EF, D3 = HI removes the fractions:
% A*D2*D3 + D*D1*D3 + G*D1*D2 = D1*D2*D3.
:- digit(a,A), digit(b,B), digit(c,C), digit(d,D), digit(e,E), digit(f,F),
   digit(g,G), digit(h,H), digit(i,I),
   D1 = 10*B + C, D2 = 10*E + F, D3 = 10*H + I,
   A*D2*D3 + D*D1*D3 + G*D1*D2 != D1*D2*D3.

% The answer: one atom per letter.
a(V) :- digit(a,V).
b(V) :- digit(b,V).
c(V) :- digit(c,V).
d(V) :- digit(d,V).
e(V) :- digit(e,V).
f(V) :- digit(f,V).
g(V) :- digit(g,V).
h(V) :- digit(h,V).
i(V) :- digit(i,V).
#show a/1.
#show b/1.
#show c/1.
#show d/1.
#show e/1.
#show f/1.
#show g/1.
#show h/1.
#show i/1.

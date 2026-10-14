% Fractions puzzle (CSPLib 041): find nine different non-zero digits A..I such
% that A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.
% The puzzle has no data.

% The three fractions and the letters of numerator, tens digit and units digit.
group(1,a,b,c). group(2,d,e,f). group(3,g,h,i).

% A candidate fraction is a numerator digit N over the two-digit denominator
% 10*P + Q, all three digits different and from 1 to 9. The reference declares
% each denominator in 1..n*n with n = 9, so a denominator is at most 81.
fraction(N,P,Q) :- N = 1..9, P = 1..9, Q = 1..9, N != P, N != Q, P != Q, 10*P + Q <= 81.
denominator(10*P + Q, P, Q) :- fraction(_,P,Q).

% Each fraction of the equation is exactly one candidate fraction.
1 { pick(K,N,P,Q) : fraction(N,P,Q) } 1 :- group(K,_,_,_).

% The letters take the digits of the picked fractions, and no digit is used twice.
digit(L,N) :- pick(K,N,_,_), group(K,L,_,_).
digit(L,P) :- pick(K,_,P,_), group(K,_,L,_).
digit(L,Q) :- pick(K,_,_,Q), group(K,_,_,L).
:- digit(L1,V), digit(L2,V), L1 < L2.

% A/BC + D/EF + G/HI = 1. Multiplied through by BC*EF, the first two fractions
% leave the remainder R/M with M = BC*EF and R = M - A*EF - D*BC, and G/HI must
% equal it: HI = G*M/R. Computing HI from G instead of trying every third
% fraction keeps the grounding to pairs of fractions times nine numerators;
% joining all three fractions in one rule body is what exhausted memory before.
closes(A,B,C,D,E,F,G,H,I) :-
    fraction(A,B,C), fraction(D,E,F),
    A != D, A != E, A != F, B != D, B != E, B != F, C != D, C != E, C != F,
    M = (10*B + C) * (10*E + F), R = M - A*(10*E + F) - D*(10*B + C), R > 0,
    G = 1..9, (G*M) \ R == 0, X = G*M / R, X <= 81,
    denominator(X,H,I), fraction(G,H,I).

% The first two picked fractions must be completed to 1 by the third.
completed(A,B,C,D,E,F) :- closes(A,B,C,D,E,F,G,H,I), pick(3,G,H,I).
:- pick(1,A,B,C), pick(2,D,E,F), not completed(A,B,C,D,E,F).

% The answer: one atom per letter, a(V), b(V), ...
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

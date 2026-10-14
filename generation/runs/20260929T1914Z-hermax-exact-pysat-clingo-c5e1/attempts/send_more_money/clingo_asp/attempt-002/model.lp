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

% SEND + MORE = MONEY, each word read as a number: SEND + MORE - MONEY = 0. The
% weighted sum is written as one aggregate; the second tuple element only keeps
% equal terms (such as the two E's) apart.
:- #sum { 1000*V,send_s : digit(s,V);  100*V,send_e : digit(e,V);  10*V,send_n : digit(n,V);  V,send_d : digit(d,V);
          1000*V,more_m : digit(m,V);  100*V,more_o : digit(o,V);  10*V,more_r : digit(r,V);  V,more_e : digit(e,V);
          -10000*V,money_m : digit(m,V);  -1000*V,money_o : digit(o,V);  -100*V,money_n : digit(n,V);
          -10*V,money_e : digit(e,V);  -V,money_y : digit(y,V) } != 0.

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

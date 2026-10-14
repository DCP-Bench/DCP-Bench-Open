% Crypta: a cryptarithmetic addition of two 20-digit numbers. Each letter is a
% different digit from 0 to 9, and no number starts with a zero.
% The puzzle is fixed by the problem; the instance carries no data.
letter(a;b;c;d;e;f;g;h;i;j).

% col(K, X, Y, Z): in column K (0 is the units) the first number has the letter X,
% the second number Y, and the total Z. The numbers are BAIJJAJIIAHFCFEBBJEA,
% DHFGABCDIDBIFFAGFEJE and GJEGACDDHFAFJBFIHEEF.
col(0,a,e,f).   col(1,e,j,e).   col(2,j,e,e).   col(3,b,f,h).   col(4,b,g,i).
col(5,e,a,f).   col(6,f,f,b).   col(7,c,f,j).   col(8,f,i,f).   col(9,h,b,a).
col(10,a,d,f).  col(11,i,i,h).  col(12,i,d,d).  col(13,j,c,d).  col(14,a,b,c).
col(15,j,a,a).  col(16,j,g,g).  col(17,i,f,e).  col(18,a,h,j).  col(19,b,d,g).

% Every letter stands for exactly one digit, and no digit is used twice.
1 { digit(L,V) : V = 0..9 } 1 :- letter(L).
:- digit(L1,V), digit(L2,V), L1 < L2.

% No number starts with a zero: the first letters are B, D and G.
:- digit(b,0).
:- digit(d,0).
:- digit(g,0).

% The addition is done column by column, from the units up. carry(K) is true when
% column K - 1 passes a carry of 1 on to column K; there is no carry into the units
% column or out of the last one.
{ carry(K) } :- K = 1..19.
% The two digits of column K plus the carry coming in = the digit of the total plus
% 10 * the carry going out.
:- col(K,_,_,_), #sum { V,first : col(K,L,_,_), digit(L,V);  V,second : col(K,_,L,_), digit(L,V);
                        1,in : carry(K);  -V,total : col(K,_,_,L), digit(L,V);  -10,out : carry(K+1) } != 0.

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
j(V) :- digit(j,V).
#show a/1.
#show b/1.
#show c/1.
#show d/1.
#show e/1.
#show f/1.
#show g/1.
#show h/1.
#show i/1.
#show j/1.

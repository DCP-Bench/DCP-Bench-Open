% General store: each letter of the sign stands for a different digit, and the
% sixteen words above the line add up to ALL WOOL.
% The puzzle is fixed by the problem; the instance carries no data.
letter(a;b;c;e;h;l;o;p;s;w).

% The words. at(N, K, L): word N has the letter L at place K, where K = 0 is the
% units place.
at(1,4,c). at(1,3,h). at(1,2,e). at(1,1,s). at(1,0,s).  % CHESS
at(2,3,c). at(2,2,a). at(2,1,s). at(2,0,h).  % CASH
at(3,5,b). at(3,4,o). at(3,3,w). at(3,2,w). at(3,1,o). at(3,0,w).  % BOWWOW
at(4,4,c). at(4,3,h). at(4,2,o). at(4,1,p). at(4,0,s).  % CHOPS
at(5,5,a). at(5,4,l). at(5,3,s). at(5,2,o). at(5,1,p). at(5,0,s).  % ALSOPS
at(6,6,p). at(6,5,a). at(6,4,l). at(6,3,e). at(6,2,a). at(6,1,l). at(6,0,e).  % PALEALE
at(7,3,c). at(7,2,o). at(7,1,o). at(7,0,l).  % COOL
at(8,3,b). at(8,2,a). at(8,1,s). at(8,0,s).  % BASS
at(9,3,h). at(9,2,o). at(9,1,p). at(9,0,s).  % HOPS
at(10,3,a). at(10,2,l). at(10,1,e). at(10,0,s).  % ALES
at(11,3,h). at(11,2,o). at(11,1,e). at(11,0,s).  % HOES
at(12,5,a). at(12,4,p). at(12,3,p). at(12,2,l). at(12,1,e). at(12,0,s).  % APPLES
at(13,3,c). at(13,2,o). at(13,1,w). at(13,0,s).  % COWS
at(14,5,c). at(14,4,h). at(14,3,e). at(14,2,e). at(14,1,s). at(14,0,e).  % CHEESE
at(15,5,c). at(15,4,h). at(15,3,s). at(15,2,o). at(15,1,a). at(15,0,p).  % CHSOAP
at(16,4,s). at(16,3,h). at(16,2,e). at(16,1,e). at(16,0,p).  % SHEEP
% The total. total(K, L): ALLWOOL has the letter L at place K.
total(6,a). total(5,l). total(4,l). total(3,w). total(2,o). total(1,o). total(0,l).  % ALLWOOL

% Every letter stands for exactly one digit, and no digit is used twice.
1 { digit(L,V) : V = 0..9 } 1 :- letter(L).
:- digit(L1,V), digit(L2,V), L1 < L2.

% The words add up to the total: the value of every word (each digit times its
% place value) minus the value of the total is zero. The word number and the place
% keep equal terms apart.
:- #sum { V*10**K,N,K : at(N,K,L), digit(L,V);  -V*10**K,total,K : total(K,L), digit(L,V) } != 0.

% The answer: one atom per letter, a(V), b(V), ...
a(V) :- digit(a,V).
b(V) :- digit(b,V).
c(V) :- digit(c,V).
e(V) :- digit(e,V).
h(V) :- digit(h,V).
l(V) :- digit(l,V).
o(V) :- digit(o,V).
p(V) :- digit(p,V).
s(V) :- digit(s,V).
w(V) :- digit(w,V).
#show a/1.
#show b/1.
#show c/1.
#show e/1.
#show h/1.
#show l/1.
#show o/1.
#show p/1.
#show s/1.
#show w/1.

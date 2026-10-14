% Age changing: starting from my age and applying the four operations +2, /8, -3, *7 in some order
% gives my husband's age; starting from his age and applying the same four operations in a different
% order gives my age. Find both ages (16 to 120 years).
% This problem has no instance data: every number below belongs to the problem statement.
age(16..120).
value(1..1000).
op(0..3).
position(0..3).

% step(O,Old,New): operation O turns the value Old into New, both between 1 and 1000 (the
% reference's range for the intermediate values). Operation 1 is the exact division by 8: New is
% such that 8*New = Old, which is what the reference requires.
step(0,Old,Old+2) :- value(Old), Old+2 <= 1000.
step(1,Old,Old/8) :- value(Old), Old \ 8 == 0, Old/8 >= 1.
step(2,Old,Old-3) :- value(Old), Old-3 >= 1.
step(3,Old,Old*7) :- value(Old), Old*7 <= 1000.

% m(A): my age is A.
1 { m(A) : age(A) } 1.

% perm1(K,O) and perm2(K,O): the K-th operation applied is O, in the order that goes from my age
% to my husband's (perm1) and from his age to mine (perm2). Each order uses every operation once.
1 { perm1(K,O) : op(O) } 1 :- position(K).
1 { perm1(K,O) : position(K) } 1 :- op(O).
1 { perm2(K,O) : op(O) } 1 :- position(K).
1 { perm2(K,O) : position(K) } 1 :- op(O).

% The two orders are different: some position has different operations.
differ :- perm1(K,O), not perm2(K,O).
:- not differ.

% hlist(K,V): the value after K operations applied to my age, in the first order; the last one is my husband's age.
hlist(0,A) :- m(A).
hlist(K+1,New) :- hlist(K,Old), perm1(K,O), step(O,Old,New).
h(V) :- hlist(4,V).
:- h(V), not age(V).

% mlist(K,V): the value after K operations applied to my husband's age, in the second order; the last one is my age.
mlist(0,V) :- h(V).
mlist(K+1,New) :- mlist(K,Old), perm2(K,O), step(O,Old,New).
:- m(A), not mlist(4,A).

% The orders of operations are not outputs, and one pair of ages can come from several orders:
% project the enumeration onto the ages.
#project m/1.
#project h/1.

#show m/1.
#show h/1.

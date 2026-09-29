% Giant cat army riddle: start from [0] and extend the list by adding 5, adding
% 7 or taking a square root, so that all numbers are different integers of at
% most 60, the list contains 2, then 10, then 14 (in that order), and it ends
% with 14 after exactly 24 numbers.
% The riddle fixes these numbers, so they are mirrored here.
max_value(60).   % largest number allowed in the list
length_of_list(24).  % number of entries in the list
goal(14).        % the last entry

index(0..L-1) :- length_of_list(L).
value(0..M) :- max_value(M).

% x(I, V): the I-th number of the list is V; all numbers are different.
1 { x(I,V) : value(V) } 1 :- index(I).
:- x(I,V), x(J,V), I < J.

% The list starts with 0 and ends with 14.
:- not x(0,0).
:- length_of_list(L), goal(G), not x(L-1,G).

% Each number follows the previous one by adding 5, adding 7, or taking the square
% root (the previous number is the square of the next one).
move(V,V+5) :- value(V), value(V+5).
move(V,V+7) :- value(V), value(V+7).
move(V*V,V) :- value(V), value(V*V).
:- x(I,V), x(I+1,W), not move(V,W).

% The list contains 2 and later 10.
:- x(J,10), not 1 <= #count { I : x(I,2), I < J }.
has_10 :- x(_,10).
:- not has_10.

#show x/2.

% Magic hexagon: place the numbers 1..19 in the 19 cells of a hexagon (rows of
% 3, 4, 5, 4, 3 cells) so that the numbers along each of the 15 lines add up to
% the same magic sum.
% The instance fields NUM_CELLS and MAGIC_SUM arrive with their first letter lowered:
% nUM_CELLS(19) and mAGIC_SUM(38).
cell(0..N-1) :- nUM_CELLS(N).
number(1..N) :- nUM_CELLS(N).

% The geometry is fixed by the problem. Cells are numbered row by row from 0:
%       0  1  2
%     3  4  5  6
%   7  8  9 10 11
%    12 13 14 15
%      16 17 18
% line(L, C): cell C lies on line L. Lines 0-4 are the horizontal rows, 5-9 the
% diagonals from top left to bottom right, 10-14 those from top right to bottom left.
line(0,(0;1;2)).
line(1,(3;4;5;6)).
line(2,(7;8;9;10;11)).
line(3,(12;13;14;15)).
line(4,(16;17;18)).
line(5,(0;3;7)).
line(6,(1;4;8;12)).
line(7,(2;5;9;13;16)).
line(8,(6;10;14;17)).
line(9,(11;15;18)).
line(10,(2;6;11)).
line(11,(1;5;10;15)).
line(12,(0;4;9;14;18)).
line(13,(3;8;13;17)).
line(14,(7;12;16)).

% Every cell holds exactly one number, and no number is used twice.
1 { lD(C,V) : number(V) } 1 :- cell(C).
:- lD(C1,V), lD(C2,V), C1 < C2.

% Every line adds up to the magic sum.
:- mAGIC_SUM(S), line(L,_), S != #sum { V,C : line(L,C), lD(C,V) }.

#show lD/2.

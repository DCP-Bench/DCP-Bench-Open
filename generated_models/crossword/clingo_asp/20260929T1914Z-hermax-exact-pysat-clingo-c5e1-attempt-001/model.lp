% Crossword: pick 8 different words from a list of 15 to fill the 8 numbered
% slots of a small crossword grid so that every place where two slots cross
% holds the same letter in both words.
% The puzzle itself is fixed by the problem, so its data is mirrored here.
% letter(W, P, L): word W (numbered from 0) has the letter number L (A = 1 .. Z = 26) at
% position P (from 0), or 0 past its end. The words, sorted longest first and then
% alphabetically: HOSES LASER SAILS SHEET STEER HEEL HIKE KEEL KNOT LINE AFT ALE EEL LEE TIE.
word(0..14).
slot(0..7).
letter(0,0,8). letter(0,1,15). letter(0,2,19). letter(0,3,5). letter(0,4,19).
letter(1,0,12). letter(1,1,1). letter(1,2,19). letter(1,3,5). letter(1,4,18).
letter(2,0,19). letter(2,1,1). letter(2,2,9). letter(2,3,12). letter(2,4,19).
letter(3,0,19). letter(3,1,8). letter(3,2,5). letter(3,3,5). letter(3,4,20).
letter(4,0,19). letter(4,1,20). letter(4,2,5). letter(4,3,5). letter(4,4,18).
letter(5,0,8). letter(5,1,5). letter(5,2,5). letter(5,3,12). letter(5,4,0).
letter(6,0,8). letter(6,1,9). letter(6,2,11). letter(6,3,5). letter(6,4,0).
letter(7,0,11). letter(7,1,5). letter(7,2,5). letter(7,3,12). letter(7,4,0).
letter(8,0,11). letter(8,1,14). letter(8,2,15). letter(8,3,20). letter(8,4,0).
letter(9,0,12). letter(9,1,9). letter(9,2,14). letter(9,3,5). letter(9,4,0).
letter(10,0,1). letter(10,1,6). letter(10,2,20). letter(10,3,0). letter(10,4,0).
letter(11,0,1). letter(11,1,12). letter(11,2,5). letter(11,3,0). letter(11,4,0).
letter(12,0,5). letter(12,1,5). letter(12,2,12). letter(12,3,0). letter(12,4,0).
letter(13,0,12). letter(13,1,5). letter(13,2,5). letter(13,3,0). letter(13,4,0).
letter(14,0,20). letter(14,1,9). letter(14,2,5). letter(14,3,0). letter(14,4,0).

% crossing(SlotA, PositionInA, SlotB, PositionInB)
crossing(0,2,1,0). crossing(0,4,2,0). crossing(3,1,1,2). crossing(3,2,4,0). crossing(3,3,2,2).
crossing(6,0,1,3). crossing(6,1,4,1). crossing(6,2,2,3). crossing(7,0,5,1). crossing(7,2,1,4).
crossing(7,3,4,2). crossing(7,4,2,4).

% e(S, W): slot S holds word W; every slot holds one word and all words are different.
1 { e(S,W) : word(W) } 1 :- slot(S).
:- e(S1,W), e(S2,W), S1 < S2.

% Where two slots cross, the two words show the same letter.
:- crossing(A,PA,B,PB), e(A,WA), e(B,WB), letter(WA,PA,LA), letter(WB,PB,LB), LA != LB.

#show e/2.

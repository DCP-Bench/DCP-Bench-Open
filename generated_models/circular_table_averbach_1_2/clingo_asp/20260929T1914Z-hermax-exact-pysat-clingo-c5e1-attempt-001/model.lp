% Averbach's card-passing riddle: three players X, Y, Z of three different
% nationalities (American, English, French) sit round a table, each passing
% three cards to the person on their right. Y passed to the American, and X
% passed to the person who passed to the Frenchwoman. Find who is who.
% A seat is 0, 1 or 2 and seat b+1 (mod 3) is to the right of seat b.
% The riddle fixes everything; the instance carries no data.

% Seats of the three players, all different.
1 { x(S) : S = 0..2 } 1.
1 { y(S) : S = 0..2 } 1.
1 { z(S) : S = 0..2 } 1.
:- x(S), y(S).
:- x(S), z(S).
:- y(S), z(S).

% Seats of the three nationalities, all different: the same seat number in the
% player and nationality outputs denotes the same person.
1 { american(S) : S = 0..2 } 1.
1 { english(S) : S = 0..2 } 1.
1 { french(S) : S = 0..2 } 1.
:- american(S), english(S).
:- american(S), french(S).
:- english(S), french(S).

% The American sits to the right of Y, since Y passed to the American.
:- american(A), y(Y), A != (Y + 1) \ 3.
% X sits to the right of the Frenchwoman, since X passed to the person who passed to her.
:- x(X), french(F), X != (F + 1) \ 3.

#show x/1.
#show y/1.
#show z/1.
#show american/1.
#show english/1.
#show french/1.

% Averbach's card-passing riddle: three players X, Y, Z of three different
% nationalities (American, English, French) sit round a table, each passing
% three cards to the person on their right. Y passed to the American, and X
% passed to the person who passed to the Frenchwoman. Find who is who.
% A seat is 0, 1 or 2 and seat b+1 (mod 3) is to the right of seat b.
include "globals.mzn";

% The riddle fixes everything; the instance carries no data.

% seats of the three players, all different
var 0..2: x;
var 0..2: y;
var 0..2: z;
constraint all_different([x, y, z]);

% seats of the three nationalities, all different: the same seat number in the
% player and nationality outputs denotes the same person
var 0..2: american;
var 0..2: english;
var 0..2: french;
constraint all_different([american, english, french]);

% the American sits to the right of Y, since Y passed to the American
constraint american = (y + 1) mod 3;
% X sits to the right of the Frenchwoman, since X passed to the person who passed to her
constraint x = (french + 1) mod 3;

solve satisfy;

output ["{\"x\": ", show(x), ", \"y\": ", show(y), ", \"z\": ", show(z),
        ", \"american\": ", show(american), ", \"english\": ", show(english),
        ", \"french\": ", show(french), "}"];

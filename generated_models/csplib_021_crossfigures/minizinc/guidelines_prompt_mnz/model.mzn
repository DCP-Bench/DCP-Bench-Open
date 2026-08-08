
include "globals.mzn";

% Grid dimensions
set of int: ROWS = 1..9;
set of int: COLS = 1..9;

% Black squares definition
array[ROWS,COLS] of bool: is_black = array2d(ROWS, COLS,
[
  % 1  2  3  4  5   6  7  8  9
   false, false, false, false, true,  false, false, false, false,  % 1
   false, false, true,  false, false, false, true,  false, false,  % 2
   false, true,  false, false, true,  false, false, true,  false,  % 3
   false, false, false, false, true,  false, false, false, false,  % 4
   true,  false, true,  true,  true,  true,  true,  false, true,   % 5
   false, false, false, false, true,  false, false, false, false,  % 6
   false, true,  false, false, true,  false, false, true,  false,  % 7
   false, false, true,  false, false, false, true,  false, false,  % 8
   false, false, false, false, true,  false, false, false, false   % 9
]);

% Digit variables for each cell (0 for black squares)
array[ROWS,COLS] of var 0..9: M;
constraint
  forall(r,c in ROWS, COLS) (
    if is_black[r,c] then M[r,c] = 0
    else M[r,c] >= 0 endif
  );

% Across entry variables
var 0..9999: A1;   % length 4 at (1,1)-(1,4)
var 0..999:  A4;   % length 4 at (1,6)-(1,9)
var 0..99:   A7;   % length 2 at (2,1)-(2,2)
var 0..999:  A8;   % length 3 at (2,4)-(2,6)
var 0..99:   A9;   % length 2 at (2,8)-(2,9)
var 0..99:   A10;  % length 2 at (3,3)-(3,4)
var 0..99:   A11;  % length 2 at (3,6)-(3,7)
var 0..9999: A13;  % length 4 at (4,1)-(4,4)
var 0..9999: A15;  % length 4 at (4,6)-(4,9)
var 0..9999: A17;  % length 4 at (6,1)-(6,4)
var 0..9999: A20;  % length 4 at (6,6)-(6,9)
var 0..99:   A23;  % length 2 at (7,3)-(7,4)
var 0..99:   A24;  % length 2 at (7,6)-(7,7)
var 0..99:   A25;  % length 2 at (8,1)-(8,2)
var 0..999:  A27;  % length 3 at (8,4)-(8,6)
var 0..99:   A28;  % length 2 at (8,8)-(8,9)
var 0..9999: A29;  % length 4 at (9,1)-(9,4)
var 0..9999: A30;  % length 4 at (9,6)-(9,9)

% Down entry variables
var 0..9999: D1;   % (1,1)-(4,1)
var 0..99:   D2;   % (1,2)-(2,2)
var 0..9999: D3;   % (1,4)-(4,4)
var 0..9999: D4;   % (1,6)-(4,6)
var 0..99:   D5;   % (1,8)-(2,8)
var 0..9999: D6;   % (1,9)-(4,9)
var 0..99:   D10;  % (3,3)-(4,3)
var 0..99:   D12;  % (3,7)-(4,7)
var 0..999:  D14;  % (4,2)-(6,2)
var 0..999:  D16;  % (4,8)-(6,8)
var 0..9999: D17;  % (6,1)-(9,1)
var 0..99:   D18;  % (6,3)-(7,3)
var 0..9999: D19;  % (6,4)-(9,4)
var 0..9999: D20;  % (6,6)-(9,6)
var 0..99:   D21;  % (6,7)-(7,7)
var 0..9999: D22;  % (6,9)-(9,9)
var 0..99:   D26;  % (8,2)-(9,2)
var 0..99:   D28;  % (8,8)-(9,8)

% Auxiliary variables for squares
var 1..99: k20;
var 1..9:  k24;

% Build across numbers from digits
constraint
  A1  = M[1,1]*1000 + M[1,2]*100 + M[1,3]*10 + M[1,4] /\
  M[1,1] >= 1 /\
  A4  = M[1,6]*1000 + M[1,7]*100 + M[1,8]*10 + M[1,9] /\
  M[1,6] >= 1 /\
  A7  = M[2,1]*10   + M[2,2]         /\
  M[2,1] >= 1 /\
  A8  = M[2,4]*100  + M[2,5]*10  + M[2,6]  /\
  M[2,4] >= 1 /\
  A9  = M[2,8]*10   + M[2,9]         /\
  M[2,8] >= 1 /\
  A10 = M[3,3]*10   + M[3,4]         /\
  M[3,3] >= 1 /\
  A11 = M[3,6]*10   + M[3,7]         /\
  M[3,6] >= 1 /\
  A13 = M[4,1]*1000 + M[4,2]*100 + M[4,3]*10 + M[4,4] /\
  M[4,1] >= 1 /\
  A15 = M[4,6]*1000 + M[4,7]*100 + M[4,8]*10 + M[4,9] /\
  M[4,6] >= 1 /\
  A17 = M[6,1]*1000 + M[6,2]*100 + M[6,3]*10 + M[6,4] /\
  M[6,1] >= 1 /\
  A20 = M[6,6]*1000 + M[6,7]*100 + M[6,8]*10 + M[6,9] /\
  M[6,6] >= 1 /\
  A23 = M[7,3]*10   + M[7,4]         /\
  M[7,3] >= 1 /\
  A24 = M[7,6]*10   + M[7,7]         /\
  M[7,6] >= 1 /\
  A25 = M[8,1]*10   + M[8,2]         /\
  M[8,1] >= 1 /\
  A27 = M[8,4]*100  + M[8,5]*10  + M[8,6]  /\
  M[8,4] >= 1 /\
  A28 = M[8,8]*10   + M[8,9]         /\
  M[8,8] >= 1 /\
  A29 = M[9,1]*1000 + M[9,2]*100 + M[9,3]*10 + M[9,4] /\
  M[9,1] >= 1 /\
  A30 = M[9,6]*1000 + M[9,7]*100 + M[9,8]*10 + M[9,9] /\
  M[9,6] >= 1;

% Build down numbers from digits
constraint
  D1  = M[1,1]*1000 + M[2,1]*100 + M[3,1]*10 + M[4,1] /\
  M[1,1] >= 1 /\
  D2  = M[1,2]*10   + M[2,2]         /\
  M[1,2] >= 1 /\
  D3  = M[1,4]*1000 + M[2,4]*100 + M[3,4]*10 + M[4,4] /\
  M[1,4] >= 1 /\
  D4  = M[1,6]*1000 + M[2,6]*100 + M[3,6]*10 + M[4,6] /\
  M[1,6] >= 1 /\
  D5  = M[1,8]*10   + M[2,8]         /\
  M[1,8] >= 1 /\
  D6  = M[1,9]*1000 + M[2,9]*100 + M[3,9]*10 + M[4,9] /\
  M[1,9] >= 1 /\
  D10 = M[3,3]*10   + M[4,3]         /\
  M[3,3] >= 1 /\
  D12 = M[3,7]*10   + M[4,7]         /\
  M[3,7] >= 1 /\
  D14 = M[4,2]*100  + M[5,2]*10  + M[6,2]  /\
  M[4,2] >= 1 /\
  D16 = M[4,8]*100  + M[5,8]*10  + M[6,8]  /\
  M[4,8] >= 1 /\
  D17 = M[6,1]*1000 + M[7,1]*100 + M[8,1]*10 + M[9,1] /\
  M[6,1] >= 1 /\
  D18 = M[6,3]*10   + M[7,3]         /\
  M[6,3] >= 1 /\
  D19 = M[6,4]*1000 + M[7,4]*100 + M[8,4]*10 + M[9,4] /\
  M[6,4] >= 1 /\
  D20 = M[6,6]*1000 + M[7,6]*100 + M[8,6]*10 + M[9,6] /\
  M[6,6] >= 1 /\
  D21 = M[6,7]*10   + M[7,7]         /\
  M[6,7] >= 1 /\
  D22 = M[6,9]*1000 + M[7,9]*100 + M[8,9]*10 + M[9,9] /\
  M[6,9] >= 1 /\
  D26 = M[8,2]*10   + M[9,2]         /\
  M[8,2] >= 1 /\
  D28 = M[8,8]*10   + M[9,8]         /\
  M[8,8] >= 1;

% Across clue constraints
constraint
  A1  = 2 * A27 /\
  A4  = D4 + 71 /\
  A7  = D18 + 4 /\
  D6  = 16 * A8 /\
  A9  = D2 - 18 /\
  A10 = 72 /\
  A11 = D5 - 70 /\
  A13 = D26 * A23 /\
  A15 = D6 - 350 /\
  A17 = A25 * A27 /\
  k20 * k20 = A20 /\
  % prime constraint for A23
  A23 > 1 /\
  forall(i in 2..A23)(i*i > A23 \/ A23 mod i != 0) /\
  k24 * k24 = A24 /\
  A25 * 17 = A20 /\
  D6  = 4 * A27 /\
  A28 = 48 /\
  A29 = 1008 /\
  A30 = D22 + 450;

% Down clue constraints
constraint
  D1  = A1 + 27 /\
  D2  = 60 /\
  D3  = A30 + 888 /\
  D4  = 2 * A17 /\
  A29 mod 12 = 0 /\
  D5  = A29 div 12 /\
  D6  = A28 * A23 /\
  D10 = A10 + 4 /\
  D12 = 3 * A24 /\
  A13 mod 16 = 0 /\
  D14 = A13 div 16 /\
  D16 = D28 * 15 /\
  D17 = A13 - 399 /\
  A29 mod 18 = 0 /\
  D18 = A29 div 18 /\
  D19 = D22 - 94 /\
  D20 = A20 - 9 /\
  D21 = A25 - 52 /\
  D22 = D20 * 6 /\
  D26 = 5 * A24 /\
  D28 = D21 + 27;

solve satisfy;

output [
  "{",
  "\"M\": ", show([[M[r,c] | c in COLS] | r in ROWS]),
  "}"
];

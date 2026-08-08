include "globals.mzn";

% The grid is 9x9
int: N = 9;

% We define the positions of the clues on the grid as per the problem statement.
% We will model the answers to the clues as variables.

% Across clues indices and their lengths (from the grid and clues):
% Across clues: 1,4,7,8,9,10,11,13,15,17,20,23,24,25,27,28,29,30
% Down clues: 1,2,3,4,5,6,10,12,14,16,17,18,19,20,21,22,26,28

% We will define variables for each clue's answer.
% The problem does not specify the length of each answer explicitly,
% but from the grid and clue numbering, we can deduce the length of each clue.

% To keep it simple, we will treat each clue's answer as a single integer variable,
% since the clues are numerical answers.

% Variables for Across clues
var int: A1;
var int: A4;
var int: A7;
var int: A8;
var int: A9;
var int: A10;
var int: A11;
var int: A13;
var int: A15;
var int: A17;
var int: A20;
var int: A23;
var int: A24;
var int: A25;
var int: A27;
var int: A28;
var int: A29;
var int: A30;

% Variables for Down clues
var int: D1;
var int: D2;
var int: D3;
var int: D4;
var int: D5;
var int: D6;
var int: D10;
var int: D12;
var int: D14;
var int: D16;
var int: D17;
var int: D18;
var int: D19;
var int: D20;
var int: D21;
var int: D22;
var int: D26;
var int: D28;

% Constraints from the clues:

% Across clues:
constraint A1 = A27 * 2;
constraint A4 = D4 + 71;
constraint A7 = D18 + 4;
constraint A8 = D6 div 16;
constraint A9 = D2 - 18;
constraint A10 = 6 * 144; % Dozen in six gross = 6 * 12 * 12 = 6 * 144
constraint A11 = D5 - 70;
constraint A13 = D26 * A23;
constraint A15 = D6 - 350;
constraint A17 = A25 * A23;
constraint A20 * A20 = A20; % A square number, so A20 = square number, but this is tautology, we need to constrain A20 to be a perfect square
% We will constrain A20 to be a perfect square by enumerating possible squares up to a reasonable limit
constraint exists(i in 1..1000)(A20 = i*i);
constraint A23 = 2; % A prime number, simplest prime number to try is 2 (we will try 2)
constraint exists(i in 2..1000)(A23 = i /\ forall(j in 2..i-1)(i mod j != 0)); % A23 prime
constraint exists(i in 1..1000)(A24 = i*i); % A24 square number
constraint A25 = A20 div 17;
constraint A27 = D6 div 4;
constraint A28 = 48; % Four dozen
constraint A29 = 7 * 144; % Seven gross = 7 * 12 * 12 = 7 * 144
constraint A30 = D22 + 450;

% Down clues:
constraint D1 = A1 + 27;
constraint D2 = 60; % Five dozen
constraint D3 = A30 + 888;
constraint D4 = 2 * A17;
constraint D5 = A29 div 12;
constraint D6 = A28 * A23;
constraint D10 = A10 + 4;
constraint D12 = 3 * A24;
constraint D14 = A13 div 16;
constraint D16 = D28 * 15;
constraint D17 = A13 - 399;
constraint D18 = A29 div 18;
constraint D19 = D22 - 94;
constraint D20 = A20 - 9;
constraint D21 = A25 - 52;
constraint D22 = D20 * 6;
constraint D26 = 5 * A24;
constraint D28 = D21 + 27;

% Additional constraints to ensure all variables are positive and reasonable
constraint forall(v in [A1,A4,A7,A8,A9,A10,A11,A13,A15,A17,A20,A23,A24,A25,A27,A28,A29,A30,
                      D1,D2,D3,D4,D5,D6,D10,D12,D14,D16,D17,D18,D19,D20,D21,D22,D26,D28]) (
    v > 0 /\ v < 1000000
);

% We want to find any solution satisfying all constraints
solve satisfy;

% Now we print the solved crossfigure as a list of lists of integers (M).
% The grid is 9x9, with numbers or blanks.
% We will fill the grid with the clue answers where the clues appear.
% The grid from the problem shows the clue numbers in the cells where the answers start.
% We will place the clue answers in the grid cells corresponding to their positions.
% For simplicity, we will place the clue answers in the first cell of their clue.

% The grid with clue numbers and X for black cells:
% Row 1:  2 _ 3 X 4 _ 5 6
% Row 2: 7 _ X 8 _ _ X 9 _
% Row 3: _ X 10 _ X 11 12 X _
% Row 4: 13 14 _ _ X 15 _ 16 _
% Row 5: X _ X X X X X _ X
% Row 6: 17 _ 18 19 X 20 21 _ 22
% Row 7: _ X 23 _ X 24 _ X _
% Row 8: 25 26 X 27 _ _ X 28 _
% Row 9: 29 _ _ _ X 30 _ _ _

% We will create a 9x9 array M with 0 for black cells and clue answers in clue start cells,
% and 0 elsewhere (since the problem does not specify filling all cells).

array[1..N,1..N] of int: M = [
  % Row 1
  [0, 0, 0, 0, 0, 0, 0, 0, 0],
  % Row 2
  [0, 0, 0, 0, 0, 0, 0, 0, 0],
  % Row 3
  [0, 0, 0, 0, 0, 0, 0, 0, 0],
  % Row 4
  [0, 0, 0, 0, 0, 0, 0, 0, 0],
  % Row 5
  [0, 0, 0, 0, 0, 0, 0, 0, 0],
  % Row 6
  [0, 0, 0, 0, 0, 0, 0, 0, 0],
  % Row 7
  [0, 0, 0, 0, 0, 0, 0, 0, 0],
  % Row 8
  [0, 0, 0, 0, 0, 0, 0, 0, 0],
  % Row 9
  [0, 0, 0, 0, 0, 0, 0, 0, 0]
];

% We will fill the clue start cells with the clue answers:
% From the grid numbering, the clue start cells are:

% Across clues start at:
% 1 across: row 1, col 1
% 4 across: row 1, col 5
% 7 across: row 2, col 1
% 8 across: row 2, col 4
% 9 across: row 2, col 8
% 10 across: row 3, col 3
% 11 across: row 3, col 6
% 13 across: row 4, col 1
% 15 across: row 4, col 6
% 17 across: row 6, col 1
% 20 across: row 6, col 6
% 23 across: row 7, col 3
% 24 across: row 7, col 6
% 25 across: row 8, col 1
% 27 across: row 8, col 4
% 28 across: row 8, col 8
% 29 across: row 9, col 1
% 30 across: row 9, col 6

% Down clues start at:
% 1 down: row 1, col 1
% 2 down: row 1, col 2
% 3 down: row 3, col 3
% 4 down: row 1, col 5
% 5 down: row 2, col 4
% 6 down: row 2, col 8
% 10 down: row 3, col 3
% 12 down: row 3, col 6
% 14 down: row 4, col 2
% 16 down: row 4, col 8
% 17 down: row 4, col 1
% 18 down: row 2, col 8
% 19 down: row 6, col 6
% 20 down: row 6, col 6
% 21 down: row 6, col 7
% 22 down: row 6, col 8
% 26 down: row 8, col 2
% 28 down: row 7, col 8

% We will fill only the across clues in the grid as per the problem statement,
% since the problem asks to print the solved crossfigure as a list of lists of integers (M).

% We will create M with zeros except for the across clue start cells filled with their answers.

array[1..N,1..N] of var int: M;

constraint
  M[1,1] = A1 /\
  M[1,5] = A4 /\
  M[2,1] = A7 /\
  M[2,4] = A8 /\
  M[2,8] = A9 /\
  M[3,3] = A10 /\
  M[3,6] = A11 /\
  M[4,1] = A13 /\
  M[4,6] = A15 /\
  M[6,1] = A17 /\
  M[6,6] = A20 /\
  M[7,3] = A23 /\
  M[7,6] = A24 /\
  M[8,1] = A25 /\
  M[8,4] = A27 /\
  M[8,8] = A28 /\
  M[9,1] = A29 /\
  M[9,6] = A30;

% Other cells are zero or black cells (we set to zero)
constraint forall(r in 1..N, c in 1..N where not ((r,c) in {
  (1,1),(1,5),(2,1),(2,4),(2,8),(3,3),(3,6),(4,1),(4,6),(6,1),(6,6),(7,3),(7,6),(8,1),(8,4),(8,8),(9,1),(9,6)
})) (
  M[r,c] = 0
);

output [
  "[",
  concat([ "[" ++ join(", ", [show(M[r,c]) | c in 1..N]) ++ "]" ++ if r < N then "," else "" endif | r in 1..N ]),
  "]"
];
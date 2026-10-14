% Crossfigure (CSPLib 21): the numerical equivalent of a crossword. A 9 x 9 grid
% has black boxes and numbered answer slots (across and down); every slot is
% filled with digits that read as a number, and the numbers must satisfy the
% clues ("27 across times two", "a square number", "a prime number", ...).
% The grid, the slots and the clues are the problem itself and have no instance
% data; they are written out below as the problem states them. M holds the
% digits, with 0 in the black boxes.

int: n = 9;      % size of the grid
int: D = 9999;   % largest number any slot can hold (at most 4 digits)

% valid[i, j] = false for the black boxes of the grid (fixed by the problem)
array[1..n, 1..n] of bool: valid = array2d(1..n, 1..n, [
    true, true, true,  true,  false, true, true, true,  true,
    true, true, false, true,  true,  true, false, true, true,
    true, false, true, true,  false, true, true, false, true,
    true, true, true,  true,  false, true, true, true,  true,
    false, true, false, false, false, false, false, true, false,
    true, true, true,  true,  false, true, true, true,  true,
    true, false, true, true,  false, true, true, false, true,
    true, true, false, true,  true,  true, false, true, true,
    true, true, true,  true,  false, true, true, true,  true]);

% the digits written in the grid; 0 in a black box
array[1..n, 1..n] of var 0..9: M;
constraint forall(i in 1..n, j in 1..n where not valid[i, j]) (M[i, j] = 0);

% across(num, len, row, col): num is the number written by the len digits that start
% in row `row` and column `col` and go across
predicate across(var int: num, int: len, int: row, int: col) =
    num = sum(i in 0..len - 1) (pow(10, len - 1 - i) * M[row, col + i]);
% down(num, len, row, col): the same, going down
predicate down(var int: num, int: len, int: row, int: col) =
    num = sum(i in 0..len - 1) (pow(10, len - 1 - i) * M[row + i, col]);

% the number in each slot, named by the clue number it has in the puzzle
var 0..D: A1; var 0..D: A4; var 0..D: A7; var 0..D: A8; var 0..D: A9; var 0..D: A10;
var 0..D: A11; var 0..D: A13; var 0..D: A15; var 0..D: A17; var 0..D: A20; var 0..D: A23;
var 0..D: A24; var 0..D: A25; var 0..D: A27; var 0..D: A28; var 0..D: A29; var 0..D: A30;
var 0..D: D1; var 0..D: D2; var 0..D: D3; var 0..D: D4; var 0..D: D5; var 0..D: D6;
var 0..D: D10; var 0..D: D12; var 0..D: D14; var 0..D: D16; var 0..D: D17; var 0..D: D18;
var 0..D: D19; var 0..D: D20; var 0..D: D21; var 0..D: D22; var 0..D: D26; var 0..D: D28;

% where each slot is: its length and the row and column of its first digit
constraint across(A1, 4, 1, 1);  constraint across(A4, 4, 1, 6);  constraint across(A7, 2, 2, 1);
constraint across(A8, 3, 2, 4);  constraint across(A9, 2, 2, 8);  constraint across(A10, 2, 3, 3);
constraint across(A11, 2, 3, 6); constraint across(A13, 4, 4, 1); constraint across(A15, 4, 4, 6);
constraint across(A17, 4, 6, 1); constraint across(A20, 4, 6, 6); constraint across(A23, 2, 7, 3);
constraint across(A24, 2, 7, 6); constraint across(A25, 2, 8, 1); constraint across(A27, 3, 8, 4);
constraint across(A28, 2, 8, 8); constraint across(A29, 4, 9, 1); constraint across(A30, 4, 9, 6);

constraint down(D1, 4, 1, 1);   constraint down(D2, 2, 1, 2);   constraint down(D3, 4, 1, 4);
constraint down(D4, 4, 1, 6);   constraint down(D5, 2, 1, 8);   constraint down(D6, 4, 1, 9);
constraint down(D10, 2, 3, 3);  constraint down(D12, 2, 3, 7);  constraint down(D14, 3, 4, 2);
constraint down(D16, 3, 4, 8);  constraint down(D17, 4, 6, 1);  constraint down(D18, 2, 6, 3);
constraint down(D19, 4, 6, 4);  constraint down(D20, 4, 6, 6);  constraint down(D21, 2, 6, 7);
constraint down(D22, 4, 6, 9);  constraint down(D26, 2, 8, 2);  constraint down(D28, 2, 8, 8);

% the squares and the primes that can be written (at most D)
function bool: is_prime(int: p) = p >= 2 /\ forall(d in 2..floor(sqrt(int2float(p)))) (p mod d != 0);
set of int: squares = {i * i | i in 1..100};
set of int: primes = {p | p in 2..D where is_prime(p)};

% Across clues
constraint A1 = 2 * A27;            %  1: 27 across times two
constraint A4 = D4 + 71;            %  4: 4 down plus seventy-one
constraint A7 = D18 + 4;            %  7: 18 down plus four
constraint 16 * A8 = D6;            %  8: 6 down divided by sixteen
constraint A9 = D2 - 18;            %  9: 2 down minus eighteen
constraint 12 * A10 = 6 * 144;      % 10: dozen in six gross
constraint A11 = D5 - 70;           % 11: 5 down minus seventy
constraint A13 = D26 * A23;         % 13: 26 down times 23 across
constraint A15 = D6 - 350;          % 15: 6 down minus 350
constraint A17 = A25 * A23;         % 17: 25 across times 23 across
constraint A20 in squares;          % 20: a square number
constraint A23 in primes;           % 23: a prime number
constraint A24 in squares;          % 24: a square number
constraint 17 * A25 = A20;          % 25: 20 across divided by seventeen
constraint 4 * A27 = D6;            % 27: 6 down divided by four
constraint A28 = 4 * 12;            % 28: four dozen
constraint A29 = 7 * 144;           % 29: seven gross
constraint A30 = D22 + 450;         % 30: 22 down plus 450

% Down clues
constraint D1 = A1 + 27;            %  1: 1 across plus twenty-seven
constraint D2 = 5 * 12;             %  2: five dozen
constraint D3 = A30 + 888;          %  3: 30 across plus 888
constraint D4 = 2 * A17;            %  4: two times 17 across
constraint 12 * D5 = A29;           %  5: 29 across divided by twelve
constraint D6 = A28 * A23;          %  6: 28 across times 23 across
constraint D10 = A10 + 4;           % 10: 10 across plus four
constraint D12 = A24 * 3;           % 12: three times 24 across
constraint 16 * D14 = A13;          % 14: 13 across divided by sixteen
constraint D16 = 15 * D28;          % 16: 28 down times fifteen
constraint D17 = A13 - 399;         % 17: 13 across minus 399
constraint 18 * D18 = A29;          % 18: 29 across divided by eighteen
constraint D19 = D22 - 94;          % 19: 22 down minus ninety-four
constraint D20 = A20 - 9;           % 20: 20 across minus nine
constraint D21 = A25 - 52;          % 21: 25 across minus fifty-two
constraint D22 = 6 * D20;           % 22: 20 down times six
constraint D26 = 5 * A24;           % 26: five times 24 across
constraint D28 = D21 + 27;          % 28: 21 down plus twenty-seven

solve satisfy;

output ["{\"M\": [", join(", ", ["[" ++ join(", ", [show(M[i, j]) | j in 1..n]) ++ "]" | i in 1..n]), "]}"];

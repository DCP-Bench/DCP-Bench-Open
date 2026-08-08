include "globals.mzn";

% Letters involved
set of int: Letters = 1..10;
enum LETTERS = {A,B,C,D,E,F,G,H,I,J};

% Map letters to indices for convenience
% A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9, J=10

% Decision variables: digits assigned to each letter
array[LETTERS] of var 0..9: digit;

% All letters have distinct digits
constraint all_different(digit);

% Extract digits for each letter for readability
var 0..9: A = digit[A];
var 0..9: B = digit[B];
var 0..9: C = digit[C];
var 0..9: D = digit[D];
var 0..9: E = digit[E];
var 0..9: F = digit[F];
var 0..9: G = digit[G];
var 0..9: H = digit[H];
var 0..9: I = digit[I];
var 0..9: J = digit[J];

% The addition is:
%   B A I J J A J I I A H F C F E B B J E A
% + D H F G A B C D I D B I F F A G F E J E
% -----------------------------------------
% = G J E G A C D D H F A F J B F I H E E F

% We will represent the numbers as arrays of letters (digits),
% from left (most significant) to right (least significant).

% Length of numbers
int: len = 21;

% Left addend digits (most significant first)
array[1..len] of var 0..9: left_num = [
    B,A,I,J,J,A,J,I,I,A,H,F,C,F,E,B,B,J,E,A
];

% Right addend digits
array[1..len] of var 0..9: right_num = [
    D,H,F,G,A,B,C,D,I,D,B,I,F,F,A,G,F,E,J,E
];

% Sum digits
array[1..len] of var 0..9: sum_num = [
    G,J,E,G,A,C,D,D,H,F,A,F,J,B,F,I,H,E,E,F
];

% Leading digits of numbers cannot be zero
constraint left_num[1] != 0;
constraint right_num[1] != 0;
constraint sum_num[1] != 0;

% We will perform addition digit by digit from right to left,
% keeping track of carry.

array[0..len] of var 0..10: carry; % carry[0] is initial carry = 0
constraint carry[0] = 0;

% For each position from right to left
constraint
  forall(i in 1..len) (
    let {
      int: pos = len - i + 1
    } in
    % sum of digits + carry_in = sum digit + 10 * carry_out
    left_num[pos] + right_num[pos] + carry[i-1] = sum_num[pos] + 10 * carry[i]
  );

% The final carry after the most significant digit must be zero
constraint carry[len] = 0;

solve satisfy;

output [
    "{",
    join(",", [
        "\"A\": " ++ show(A),
        "\"B\": " ++ show(B),
        "\"C\": " ++ show(C),
        "\"D\": " ++ show(D),
        "\"E\": " ++ show(E),
        "\"F\": " ++ show(F),
        "\"G\": " ++ show(G),
        "\"H\": " ++ show(H),
        "\"I\": " ++ show(I),
        "\"J\": " ++ show(J)
    ]),
    "}"
];

include "globals.mzn";

% Decision variables: each letter is a digit 0..9
var 0..9: A;
var 0..9: B;
var 0..9: C;
var 0..9: D;
var 0..9: E;
var 0..9: F;
var 0..9: G;
var 0..9: H;
var 0..9: I;
var 0..9: J;

% All letters must be distinct
constraint all_different([A,B,C,D,E,F,G,H,I,J]);

% Represent each 20‐digit number as an array of digits, least significant first
array[1..20] of var 0..9: row1 = [
    A, E, J, B, B, E, F, C, F, H,
    A, I, I, J, A, J, J, I, A, B
];
array[1..20] of var 0..9: row2 = [
    E, J, E, F, G, A, F, F, I, B,
    D, I, D, C, B, A, G, F, H, D
];
array[1..20] of var 0..9: row3 = [
    F, E, E, H, I, F, B, J, F, A,
    F, H, D, D, C, A, G, E, J, G
];

% Carry bits for each column (carry[1] into least significant, carry[21] out of most)
array[1..21] of var 0..1: carry;
constraint carry[1] = 0;
constraint carry[21] = 0;

% Column‐wise addition with carries
constraint
  forall(i in 1..20) (
    row1[i] + row2[i] + carry[i]
    = row3[i] + 10 * carry[i+1]
  );

% No leading zeros on the most significant digit of each number
constraint B != 0;
constraint D != 0;
constraint G != 0;

solve satisfy;

% Output mapping each letter to its digit in JSON format
output [
  "{",
    "\"A\": " ++ show(A) ++ ",",
    "\"B\": " ++ show(B) ++ ",",
    "\"C\": " ++ show(C) ++ ",",
    "\"D\": " ++ show(D) ++ ",",
    "\"E\": " ++ show(E) ++ ",",
    "\"F\": " ++ show(F) ++ ",",
    "\"G\": " ++ show(G) ++ ",",
    "\"H\": " ++ show(H) ++ ",",
    "\"I\": " ++ show(I) ++ ",",
    "\"J\": " ++ show(J),
  "}"
];

include "globals.mzn";

% Given fixed values
int: A = 16;
int: B = 2;
int: F = 8;
int: G = 14;

% The 10 squares: A, B, C, D, E, F, G, H, I, K
% A, B, F, G are fixed, others are variables
array[1..10] of var 1..99: X;

% Index mapping for clarity
% 1:A, 2:B, 3:C, 4:D, 5:E, 6:F, 7:G, 8:H, 9:I, 10:K

constraint X[1] = A;
constraint X[2] = B;
constraint X[6] = F;
constraint X[7] = G;

% All numbers must be distinct
constraint alldifferent(X);

% Define a function for square
function var int: sq(var int: x) = x*x;

% The sum of squares of any two adjacent numbers equals the sum of squares of the two numbers diametrically opposite
% The circle is arranged as: A(1), B(2), C(3), D(4), E(5), F(6), G(7), H(8), I(9), K(10)
% Adjacents and their opposite pairs:
% (A,B) opposite (F,E) => (1,2) opposite (6,5)
% (B,C) opposite (G,H) => (2,3) opposite (7,8)
% (C,D) opposite (H,I) => (3,4) opposite (8,9)
% (D,E) opposite (I,K) => (4,5) opposite (9,10)
% (E,F) opposite (K,A) => (5,6) opposite (10,1)
% (F,G) opposite (A,B) => (6,7) opposite (1,2)
% (G,H) opposite (B,C) => (7,8) opposite (2,3)
% (H,I) opposite (C,D) => (8,9) opposite (3,4)
% (I,K) opposite (D,E) => (9,10) opposite (4,5)
% (K,A) opposite (E,F) => (10,1) opposite (5,6)

% Note: The problem states "any two adjoining squares in the circle" and their opposite pairs.
% The pairs repeat because the circle has 10 squares, so we only need to enforce the 5 unique pairs:
% (A,B) = (F,E)
% (B,C) = (G,H)
% (C,D) = (H,I)
% (D,E) = (I,K)
% (E,F) = (K,A)

constraint sq(X[1]) + sq(X[2]) = sq(X[6]) + sq(X[5]);
constraint sq(X[2]) + sq(X[3]) = sq(X[7]) + sq(X[8]);
constraint sq(X[3]) + sq(X[4]) = sq(X[8]) + sq(X[9]);
constraint sq(X[4]) + sq(X[5]) = sq(X[9]) + sq(X[10]);
constraint sq(X[5]) + sq(X[6]) = sq(X[10]) + sq(X[1]);

% Domain constraints: numbers are positive integers with at most two digits (1..99)
% Already defined in variable domain

solve satisfy;

output [
    "{",
    join(",", [
        "\"A\": " ++ show(X[1]),
        "\"B\": " ++ show(X[2]),
        "\"C\": " ++ show(X[3]),
        "\"D\": " ++ show(X[4]),
        "\"E\": " ++ show(X[5]),
        "\"F\": " ++ show(X[6]),
        "\"G\": " ++ show(X[7]),
        "\"H\": " ++ show(X[8]),
        "\"I\": " ++ show(X[9]),
        "\"K\": " ++ show(X[10])
    ]),
    "}"
];
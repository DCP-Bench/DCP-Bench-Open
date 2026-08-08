include "globals.mzn";

% Positions:
% C = circle, F = square
% Layout:
%   C F C
%   F   F
%   C F C

% We have 8 positions: 4 circles (C) and 4 squares (F)
% Let's name them as follows:
% Circles: c1, c2, c3, c4
% Squares: f1, f2, f3, f4

% Adjacencies (each square is adjacent to two circles):
% f1 adjacent to c1 and c2
% f2 adjacent to c2 and c3
% f3 adjacent to c3 and c4
% f4 adjacent to c4 and c1

% All digits 1..8 used exactly once

array[1..4] of var 1..8: c; % circles c[1..4]
array[1..4] of var 1..8: f; % squares f[1..4]

% All digits 1..8 used exactly once
constraint alldifferent(c ++ f);

% Each square equals sum of its two adjacent circles
constraint f[1] = c[1] + c[2];
constraint f[2] = c[2] + c[3];
constraint f[3] = c[3] + c[4];
constraint f[4] = c[4] + c[1];

% Since f[i] must be in 1..8, and sum of two circles can be up to 16,
% but f[i] domain is 1..8, so we need to relax f domain to 2..16
% because sum of two circles can be from 1+2=3 to 7+8=15
% But problem states digits 1..8 in all positions, so squares must be digits 1..8
% So sum of two circles must be in 1..8, which is only possible if circles are small numbers.
% This is contradictory because sum of two circles can be up to 15.
% So the problem likely means that the squares contain digits 1..8, but the sum constraint is that the square's number equals the sum of the two adjacent circles.
% So squares can be numbers from 2 to 16, but digits 1..8 must be placed in circles and squares.
% So squares must be digits 1..8, but sum of two circles must equal that digit.
% So sum of two circles must be in 1..8.
% So circles must be small enough to satisfy this.

% So we keep domain of f as 1..8, c as 1..8, alldifferent over all 8 variables.

solve satisfy;

output [
    "{",
    join(",", [
        "\"positions\" : {",
        "  \"c1\": " ++ show(c[1]) ++ ",",
        "  \"f1\": " ++ show(f[1]) ++ ",",
        "  \"c2\": " ++ show(c[2]) ++ ",",
        "  \"f2\": " ++ show(f[2]) ++ ",",
        "  \"c3\": " ++ show(c[3]) ++ ",",
        "  \"f3\": " ++ show(f[3]) ++ ",",
        "  \"c4\": " ++ show(c[4]) ++ ",",
        "  \"f4\": " ++ show(f[4]),
        "}"
    ]),
    "}"
];
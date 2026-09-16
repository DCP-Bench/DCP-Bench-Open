% Dudeney numbers: a perfect cube whose digits sum to its cube root.
include "globals.mzn";

int: n;

array[1..n] of var 0..9: number_digits;
var 0..pow(10, n) - 1: number;
var 1..9*n: cube_root;

constraint number = cube_root * cube_root * cube_root;
constraint cube_root = sum(i in 1..n) (number_digits[i]);
constraint number = sum(i in 1..n) (number_digits[i] * pow(10, n - i));
constraint number > 1;

solve satisfy;

output ["{\"number\": ", show(number), "}"];

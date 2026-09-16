% Curious number: one more than it is a square, and one more than its half is a
% square too - and it is not 48, which is the known example.
var 1..10000: peculiar;
var 1..10000: a; var 1..10000: b;
var 1..10000: c; var 1..10000: d; var 1..10000: e;

constraint peculiar != 48;
constraint peculiar + 1 = a;
constraint a = b * b;
constraint peculiar = 2 * c;
constraint c + 1 = d;
constraint d = e * e;

solve satisfy;

output ["{\"peculiar\": ", show(peculiar), "}"];

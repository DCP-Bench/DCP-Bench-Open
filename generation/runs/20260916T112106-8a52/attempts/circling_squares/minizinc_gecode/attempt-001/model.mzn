% Circling the squares: ten different numbers around a circle where any two
% adjacent squares sum to the same as the two diametrically opposite.
% The array runs A B C D E F G H I K.
include "globals.mzn";

array[1..10] of var 1..99: x;

constraint all_different(x);
% The four numbers given as examples: A, B, F and G.
constraint x[1] = 16;
constraint x[2] = 2;
constraint x[6] = 8;
constraint x[7] = 14;

predicate balanced(var int: p, var int: q, var int: r, var int: s) =
    p * p + q * q = r * r + s * s;

constraint balanced(x[1], x[2], x[6], x[7]);
constraint balanced(x[2], x[3], x[7], x[8]);
constraint balanced(x[3], x[4], x[8], x[9]);
constraint balanced(x[4], x[5], x[9], x[10]);
constraint balanced(x[5], x[6], x[10], x[1]);

solve satisfy;

output ["{\"A\": ", show(x[1]), ", \"B\": ", show(x[2]), ", \"C\": ", show(x[3]),
        ", \"D\": ", show(x[4]), ", \"E\": ", show(x[5]), ", \"F\": ", show(x[6]),
        ", \"G\": ", show(x[7]), ", \"H\": ", show(x[8]), ", \"I\": ", show(x[9]),
        ", \"K\": ", show(x[10]), "}"];

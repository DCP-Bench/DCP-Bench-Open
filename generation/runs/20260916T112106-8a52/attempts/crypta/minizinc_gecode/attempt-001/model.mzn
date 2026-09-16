% Crypta: a twenty-letter cryptarithmetic addition over ten distinct digits,
% checked seven digits at a time with two carries between blocks.
include "globals.mzn";

var 0..9: A; var 0..9: B; var 0..9: C; var 0..9: D; var 0..9: E;
var 0..9: F; var 0..9: G; var 0..9: H; var 0..9: I; var 0..9: J;
var 0..1: Sr1; var 0..1: Sr2;

constraint all_different([A, B, C, D, E, F, G, H, I, J]);
% No number may start with a zero.
constraint B >= 1 /\ D >= 1 /\ G >= 1;

constraint A + 10 * E + 100 * J + 1000 * B + 10000 * B + 100000 * E
         + 1000000 * F + E + 10 * J + 100 * E + 1000 * F + 10000 * G
         + 100000 * A + 1000000 * F
         = F + 10 * E + 100 * E + 1000 * H + 10000 * I + 100000 * F
         + 1000000 * B + 10000000 * Sr1;

constraint C + 10 * F + 100 * H + 1000 * A + 10000 * I + 100000 * I
         + 1000000 * J + F + 10 * I + 100 * B + 1000 * D + 10000 * I
         + 100000 * D + 1000000 * C + Sr1
         = J + 10 * F + 100 * A + 1000 * F + 10000 * H + 100000 * D
         + 1000000 * D + 10000000 * Sr2;

constraint A + 10 * J + 100 * J + 1000 * I + 10000 * A + 100000 * B + B
         + 10 * A + 100 * G + 1000 * F + 10000 * H + 100000 * D + Sr2
         = C + 10 * A + 100 * G + 1000 * E + 10000 * J + 100000 * G;

solve satisfy;

output ["{\"A\": ", show(A), ", \"B\": ", show(B), ", \"C\": ", show(C),
        ", \"D\": ", show(D), ", \"E\": ", show(E), ", \"F\": ", show(F),
        ", \"G\": ", show(G), ", \"H\": ", show(H), ", \"I\": ", show(I),
        ", \"J\": ", show(J), "}"];

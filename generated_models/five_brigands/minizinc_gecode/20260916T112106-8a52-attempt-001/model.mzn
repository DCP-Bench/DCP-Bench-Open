% Five brigands: 200 doubloons shared so that the reweighted shares also come
% to 200. Multiplying by six clears the halves and thirds.
var 1..200: A; var 1..200: B; var 1..200: C; var 1..200: D; var 1..200: E;

constraint A + B + C + D + E = 200;
constraint 6 * (A * 12 + B * 3 + C) + 3 * D + 2 * E = 6 * 200;

solve satisfy;

output ["{\"A\": ", show(A), ", \"B\": ", show(B), ", \"C\": ", show(C),
        ", \"D\": ", show(D), ", \"E\": ", show(E), "}"];

% Hanging weights: thirteen weights A..M hang from a system of bars. Each weight
% is a different integer between 1 and 13, and the weights must make every bar
% balance: the weights on either side of a pivot point are equal when weighted by
% their distance from the pivot, and a bar hanging beneath another one counts as a
% single weight equal to its total. This problem has no instance data: the
% diagram is part of the problem statement.
include "globals.mzn";

int: N = 13;

% the weights, each between 1 and 13 and different from all others
var 1..N: a; var 1..N: b; var 1..N: c; var 1..N: d; var 1..N: e; var 1..N: f; var 1..N: g;
var 1..N: h; var 1..N: i; var 1..N: j; var 1..N: k; var 1..N: l; var 1..N: m;
constraint all_different([a, b, c, d, e, f, g, h, i, j, k, l, m]);

% the bar carrying A and B balances: 4*A = B
constraint 4 * a = b;
% the bar carrying C and D balances: 5*C = D
constraint 5 * c = d;
% the bar carrying E and F balances: 3*E = 2*F
constraint 3 * e = 2 * f;
% the bar carrying G, and the bar of C and D hanging from it as a single weight
% C + D, balances: 3*G = 2*(C+D)
constraint 3 * g = 2 * (c + d);
% the bar carrying J and K, with the bar of A and B hanging on its left (A + B at
% distance 3) and the bar of G, C and D hanging on its right (G + C + D at distance 2)
% balances: 3*(A+B) + 2*J = K + 2*(G+C+D)
constraint 3 * (a + b) + 2 * j = k + 2 * (g + c + d);
% the bar carrying H and I, with the bar of E and F hanging beneath, balances:
% 3*H = 2*(E+F) + 3*I
constraint 3 * h = 2 * (e + f) + 3 * i;
% the bar carrying L and M, with the bar of H, I, E and F hanging beneath, balances:
% H+I+E+F = L + 4*M
constraint h + i + e + f = l + 4 * m;
% the top bar balances: 4*(L+M+H+I+E+F) = 3*(J+K+G+A+B+C+D)
constraint 4 * (l + m + h + i + e + f) = 3 * (j + k + g + a + b + c + d);

solve satisfy;

output ["{\"a\": ", show(a), ", \"b\": ", show(b), ", \"c\": ", show(c), ", \"d\": ", show(d),
        ", \"e\": ", show(e), ", \"f\": ", show(f), ", \"g\": ", show(g), ", \"h\": ", show(h),
        ", \"i\": ", show(i), ", \"j\": ", show(j), ", \"k\": ", show(k), ", \"l\": ", show(l),
        ", \"m\": ", show(m), "}"];

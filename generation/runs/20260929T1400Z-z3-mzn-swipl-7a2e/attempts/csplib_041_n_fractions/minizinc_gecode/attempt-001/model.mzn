% Fractions puzzle: find nine different non-zero digits A..I such that
% A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.
include "globals.mzn";

% The puzzle has no data.

% the nine digits, all different and non-zero
var 1..9: A; var 1..9: B; var 1..9: C;
var 1..9: D; var 1..9: E; var 1..9: F;
var 1..9: G; var 1..9: H; var 1..9: I;
constraint all_different([A, B, C, D, E, F, G, H, I]);

% the three denominators BC, EF, HI as two-digit numbers
var 11..99: D1 = 10 * B + C;
var 11..99: D2 = 10 * E + F;
var 11..99: D3 = 10 * H + I;

% Multiplying the equation A/D1 + D/D2 + G/D3 = 1 through by D1*D2*D3 gives
% A*D2*D3 + D*D1*D3 + G*D1*D2 = D1*D2*D3, which avoids fractions.
constraint A * D2 * D3 + D * D1 * D3 + G * D1 * D2 = D1 * D2 * D3;

solve satisfy;

output ["{\"A\": ", show(A), ", \"B\": ", show(B), ", \"C\": ", show(C), ", \"D\": ", show(D),
        ", \"E\": ", show(E), ", \"F\": ", show(F), ", \"G\": ", show(G), ", \"H\": ", show(H),
        ", \"I\": ", show(I), "}"];

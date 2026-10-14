% Send more money: each letter stands for one digit, different letters for
% different digits, and SEND + MORE = MONEY, with no leading zero.
include "globals.mzn";

% the digit (0..9) each letter stands for
var 0..9: s;
var 0..9: e;
var 0..9: n;
var 0..9: d;
var 0..9: m;
var 0..9: o;
var 0..9: r;
var 0..9: y;

% different letters stand for different digits
constraint all_different([s, e, n, d, m, o, r, y]);

% SEND + MORE = MONEY, each word read as a decimal number
constraint 1000 * s + 100 * e + 10 * n + d
         + 1000 * m + 100 * o + 10 * r + e
         = 10000 * m + 1000 * o + 100 * n + 10 * e + y;

% the first letter of each word cannot be zero
constraint s > 0 /\ m > 0;

solve satisfy;

output ["{\"s\": ", show(s), ", \"e\": ", show(e), ", \"n\": ", show(n), ", \"d\": ", show(d),
        ", \"m\": ", show(m), ", \"o\": ", show(o), ", \"r\": ", show(r), ", \"y\": ", show(y), "}"];

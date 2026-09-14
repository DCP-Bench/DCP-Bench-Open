int: n;
bool: optimize;
var 0..n: x;
var 0..n: y;
constraint if optimize then x+y >= n else x+y = n endif;
var int: objective = if optimize then x+y else 0 endif;
solve minimize objective;
output ["{\"x\":", show(x), ",\"y\":", show(y), "}"];

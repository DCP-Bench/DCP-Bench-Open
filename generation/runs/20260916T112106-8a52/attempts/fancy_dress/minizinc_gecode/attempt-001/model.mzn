% Fancy dress: the cheapest way for Mr Greenguest to attend, either by dressing
% to the rules or by paying the entrance fee. He already owns the shirt, so
% only the tie, hat, socks and fee cost anything.
var bool: t; var bool: h; var bool: r; var bool: s; var bool: n;
var 0..100: cost;

% 1. A green tie needs a green shirt.
constraint (t -> r) \/ n;
% 2. Green socks or a green shirt need a green tie or a green hat.
constraint ((s \/ r) -> (t \/ h)) \/ n;
% 3. A green shirt, a green hat, or no green socks needs a green tie.
constraint (r \/ h \/ not s) -> (t \/ n);

constraint cost = 10 * bool2int(t) + 2 * bool2int(h)
                + 12 * bool2int(s) + 11 * bool2int(n);

var int: objective = cost;
solve minimize objective;

output ["{\"t\": ", show(t), ", \"h\": ", show(h), ", \"r\": ", show(r),
        ", \"s\": ", show(s), ", \"n\": ", show(n), "}"];

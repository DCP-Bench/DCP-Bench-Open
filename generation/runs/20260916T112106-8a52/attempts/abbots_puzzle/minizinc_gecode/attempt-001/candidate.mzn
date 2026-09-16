% Abbot puzzle: share 100 bushels among 100 people. The problem carries no
% instance data, so every number here is the puzzle statement.
var 0..100: men;
var 0..100: women;
var 0..100: children;

constraint men + women + children = 100;
% Doubled through so the half-bushel child stays an integer.
constraint 6 * men + 4 * women + children = 200;
constraint 5 * men = women;

solve satisfy;

output ["{\"men\": ", show(men), ", \"women\": ", show(women),
        ", \"children\": ", show(children), "}"];

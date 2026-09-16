% Dinner: twenty people for twenty dollars, prices doubled through so the
% fifty-cent child stays an integer.
var 1..6: grandparents;
var 1..10: parents;
var 1..40: children;

constraint 6 * grandparents + 4 * parents + children = 40;
constraint grandparents + parents + children = 20;

solve satisfy;

output ["{\"grandparents\": ", show(grandparents), ", \"parents\": ", show(parents),
        ", \"children\": ", show(children), "}"];

% Variables representing the number of men, women, and children
var 0..100: men;
var 0..100: women;
var 0..100: children;

% Constraints
constraint men + women + children == 100; % total people
constraint women == 5 * men; % five times as many women as men
constraint 3 * men + 2 * women + children div 2 == 100; % total bushels distributed
constraint children mod 2 == 0; % children count must be even because each child gets half bushel

solve satisfy;

output [
    "{",
    "\"men\": ", show(men), ",",
    "\"women\": ", show(women), ",",
    "\"children\": ", show(children),
    "}"
];
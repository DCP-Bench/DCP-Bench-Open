% Include necessary library
include "globals.mzn";

% Define the domain for each person's charge (assuming positive costs up to 10000)
var 0..10000: paper_hanger;
var 0..10000: painter;
var 0..10000: plumber;
var 0..10000: electrician;
var 0..10000: carpenter;
var 0..10000: mason;

% Constraints based on the given sums
constraint paper_hanger + painter = 1100;
constraint painter + plumber = 1700;
constraint plumber + electrician = 1100;
constraint electrician + carpenter = 3300;
constraint carpenter + mason = 5300;
constraint mason + painter = 3200;

solve satisfy;

output [
    "{",
    "\"paper_hanger\": ", show(paper_hanger), ",",
    "\"painter\": ", show(painter), ",",
    "\"plumber\": ", show(plumber), ",",
    "\"electrician\": ", show(electrician), ",",
    "\"carpenter\": ", show(carpenter), ",",
    "\"mason\": ", show(mason),
    "}"
];
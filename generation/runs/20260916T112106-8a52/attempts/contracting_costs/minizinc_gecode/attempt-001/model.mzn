% Contracting costs: six tradesmen, six pairwise bills.
var 1..5300: paper_hanger; var 1..5300: painter; var 1..5300: plumber;
var 1..5300: electrician; var 1..5300: carpenter; var 1..5300: mason;

constraint paper_hanger + painter = 1100;
constraint painter + plumber = 1700;
constraint plumber + electrician = 1100;
constraint electrician + carpenter = 3300;
constraint carpenter + mason = 5300;
constraint mason + painter = 3200;

solve satisfy;

output ["{\"paper_hanger\": ", show(paper_hanger), ", \"painter\": ", show(painter),
        ", \"plumber\": ", show(plumber), ", \"electrician\": ", show(electrician),
        ", \"carpenter\": ", show(carpenter), ", \"mason\": ", show(mason), "}"];

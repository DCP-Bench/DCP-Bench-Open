% Production planning: whole numbers of chairs and tables to maximise
% profit. Each chair needs 2 labour hours and 1 board; each table needs
% 4 labour hours and 1 board. There are 40 hours and 12 boards.
var 0..40: chairs;
var 0..40: tables;

var int: profit = 15 * chairs + 25 * tables;

constraint 2 * chairs + 4 * tables <= 40;   % labour hours
constraint chairs + tables <= 12;           % boards

solve maximize profit;

output ["chairs = ", show(chairs), "\n",
        "tables = ", show(tables), "\n",
        "profit = ", show(profit), "\n"];

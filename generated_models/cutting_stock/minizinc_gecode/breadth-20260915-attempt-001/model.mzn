include "globals.mzn";

int: roll_width;
array[int] of int: widths;
array[int] of int: orders;
int: num_patterns;
array[int, int] of int: num_rolls_width;

set of int: Patterns = 1..num_patterns;
set of int: Widths = index_set(widths);
array[Patterns] of var 0..100: patterns_used;

constraint forall(i in Widths) (
    sum(j in Patterns) (num_rolls_width[j, i] * patterns_used[j]) >= orders[i]);

var int: objective = sum(j in Patterns) (patterns_used[j]);
solve minimize objective;

output ["{\"patterns_used\": [", join(", ", [show(patterns_used[j]) | j in Patterns]),
        "], \"min_rolls_cut\": ", show(objective), "}"];

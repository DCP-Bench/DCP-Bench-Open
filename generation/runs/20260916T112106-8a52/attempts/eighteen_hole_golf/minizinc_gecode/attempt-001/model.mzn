% Eighteen hole golf: eighteen holes of length three, four or five that add up
% to a par of seventy-two.
array[1..18] of var 3..5: holes;

constraint sum(holes) = 72;

solve satisfy;

output ["{\"holes\": [", join(", ", [show(holes[i]) | i in 1..18]), "]}"];

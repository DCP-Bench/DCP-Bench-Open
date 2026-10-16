Problem: a farmer has cows numbered 1..num_cows, cow c gives c units of milk. Distribute cows to num_sons sons so each son gets the given number of cows (cows_per_son) and the same total milk.

- "cows numbered from 1 up to the total number of cows" -> cow c+1 gives milk c+1; gives[c][i] Boolean per cow and son
- "each cow goes to one son" / cow_assignments -> boolsIntChanneling(gives[c], son[c], 0) (exactly one son per cow)
- "distribute according to a given distribution" -> son i gets cows_per_son[i] cows -> sum(gives[.][i]) = cows_per_son[i]
- "total quantity of milk should be the same for each son" -> total_milk = num_cows*(num_cows+1)/2 split over num_sons -> scalar(gives[.][i], milk, "=", total/num_sons)
- objective: none (satisfaction)
- search: Booleans, largest cows first

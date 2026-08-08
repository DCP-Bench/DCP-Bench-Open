
include "globals.mzn";

% Enumerations for attributes
enum COLORS = { yellow, green, red, white, blue };
enum NATIONS = { italy, spain, japan, england, norway };
enum PETS = { cat, zebra, bear, snails, horse };
enum DRINKS = { milk, water, tea, coffee, juice };
enum JOBS = { painter, sculptor, diplomat, pianist, doctor };

% Decision variables: house number (1..5) for each attribute
array[COLORS] of var 1..5: colors;
array[NATIONS] of var 1..5: nations;
array[PETS] of var 1..5: pets;
array[DRINKS] of var 1..5: drinks;
array[JOBS] of var 1..5: jobs;

% All houses must be different for each attribute category
constraint all_different(colors);
constraint all_different(nations);
constraint all_different(pets);
constraint all_different(drinks);
constraint all_different(jobs);

% Puzzle constraints:
% 1. The painter owns the horse
constraint jobs[painter] = pets[horse];
% 2. The diplomat drinks coffee
constraint jobs[diplomat] = drinks[coffee];
% 3. The one who drinks milk lives in the white house
constraint drinks[milk] = colors[white];
% 4. The Spaniard is a painter
constraint nations[spain] = jobs[painter];
% 5. The Englishman lives in the red house
constraint nations[england] = colors[red];
% 6. The snails are owned by the sculptor
constraint pets[snails] = jobs[sculptor];
% 7. The green house is directly to the left of the red one
constraint colors[green] + 1 = colors[red];
% 8. The Norwegian lives directly to the right of the blue house
constraint nations[norway] = colors[blue] + 1;
% 9. The doctor drinks milk
constraint jobs[doctor] = drinks[milk];
% 10. The diplomat is Japanese
constraint jobs[diplomat] = nations[japan];
% 11. The Norwegian owns the zebra
constraint nations[norway] = pets[zebra];
% 12. The green house is next to the white one
constraint abs(colors[green] - colors[white]) = 1;
% 13. The horse is owned by the neighbor of the diplomat
constraint abs(pets[horse] - jobs[diplomat]) = 1;
% 14. The Italian lives in the red, white, or green house
constraint
    nations[italy] = colors[red]
 \/ nations[italy] = colors[white]
 \/ nations[italy] = colors[green];

solve satisfy;

output [
    "{",
    join(",", [
      "\"colors\":[" ++ join(",", [show(colors[c]) | c in COLORS]) ++ "]",
      "\"nations\":[" ++ join(",", [show(nations[n]) | n in NATIONS]) ++ "]",
      "\"jobs\":[" ++ join(",", [show(jobs[j]) | j in JOBS]) ++ "]",
      "\"pets\":[" ++ join(",", [show(pets[p]) | p in PETS]) ++ "]",
      "\"drinks\":[" ++ join(",", [show(drinks[d]) | d in DRINKS]) ++ "]"
    ]),
    "}"
];

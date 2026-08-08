include "globals.mzn";

% Sets and indices
set of int: Houses = 1..5;

% Enumerations for attributes
enum Colors = {yellow, green, red, white, blue};
enum Nations = {italy, spain, japan, england, norway};
enum Pets = {cat, zebra, bear, snails, horse};
enum Drinks = {milk, water, tea, coffee, juice};
enum Jobs = {painter, sculptor, diplomat, pianist, doctor};

% Decision variables: position of each attribute in the houses (1..5)
array[Colors] of var Houses: color_pos;
array[Nations] of var Houses: nation_pos;
array[Pets] of var Houses: pet_pos;
array[Drinks] of var Houses: drink_pos;
array[Jobs] of var Houses: job_pos;

% All attributes in each category must be assigned to different houses
constraint alldifferent([color_pos[c] | c in Colors]);
constraint alldifferent([nation_pos[n] | n in Nations]);
constraint alldifferent([pet_pos[p] | p in Pets]);
constraint alldifferent([drink_pos[d] | d in Drinks]);
constraint alldifferent([job_pos[j] | j in Jobs]);

% Constraints from the puzzle

% The painter owns the horse
constraint job_pos[painter] = pet_pos[horse];

% The diplomat drinks coffee
constraint job_pos[diplomat] = drink_pos[coffee];

% The one who drinks milk lives in the white house
constraint drink_pos[milk] = color_pos[white];

% The Spaniard is a painter
constraint nation_pos[spain] = job_pos[painter];

% The Englishman lives in the red house
constraint nation_pos[england] = color_pos[red];

% The snails are owned by the sculptor
constraint pet_pos[snails] = job_pos[sculptor];

% The green house is on the left of the red one
constraint color_pos[green] + 1 = color_pos[red];

% The Norwegian lives on the right of the blue house
constraint nation_pos[norway] = color_pos[blue] + 1;

% The doctor drinks milk
constraint job_pos[doctor] = drink_pos[milk];

% The diplomat is Japanese
constraint job_pos[diplomat] = nation_pos[japan];

% The Norwegian owns the zebra
constraint nation_pos[norway] = pet_pos[zebra];

% The green house is next to the white one
constraint abs(color_pos[green] - color_pos[white]) = 1;

% The horse is owned by the neighbor of the diplomat
constraint abs(pet_pos[horse] - job_pos[diplomat]) = 1;

% The Italian either lives in the red, white or green house
constraint nation_pos[italy] = color_pos[red] \/
          nation_pos[italy] = color_pos[white] \/
          nation_pos[italy] = color_pos[green];

% Output the house numbers for each attribute category
solve satisfy;

output [
    "{",
    "\"colors\": ", show([color_pos[c] | c in Colors]), ",",
    "\"nations\": ", show([nation_pos[n] | n in Nations]), ",",
    "\"jobs\": ", show([job_pos[j] | j in Jobs]), ",",
    "\"pets\": ", show([pet_pos[p] | p in Pets]), ",",
    "\"drinks\": ", show([drink_pos[d] | d in Drinks]),
    "}"
];
% Zebra puzzle (Einstein's puzzle): five houses in a row, numbered 0..4 from left
% to right. Each house has a different color, and one inhabitant with a different
% nationality, pet, drink and job. From the clues, find which house goes with
% every color, nationality, job, pet and drink. Each array below is indexed by the
% item and holds the house (0..4) it belongs to; the same house number in two
% arrays means the same house.
include "globals.mzn";

int: n_houses = 5;                  % fixed by the problem statement
set of int: Houses = 0..n_houses - 1;

% house of each color, in the order yellow, green, red, white, blue
array[1..n_houses] of var Houses: colors;
% house of each nationality: italy, spain, japan, england, norway
array[1..n_houses] of var Houses: nations;
% house of each job: painter, sculptor, diplomat, pianist, doctor
array[1..n_houses] of var Houses: jobs;
% house of each pet: cat, zebra, bear, snails, horse
array[1..n_houses] of var Houses: pets;
% house of each drink: milk, water, tea, coffee, juice
array[1..n_houses] of var Houses: drinks;

var Houses: yellow = colors[1];
var Houses: green = colors[2];
var Houses: red = colors[3];
var Houses: white = colors[4];
var Houses: blue = colors[5];

var Houses: italy = nations[1];
var Houses: spain = nations[2];
var Houses: japan = nations[3];
var Houses: england = nations[4];
var Houses: norway = nations[5];

var Houses: painter = jobs[1];
var Houses: sculptor = jobs[2];
var Houses: diplomat = jobs[3];
var Houses: pianist = jobs[4];
var Houses: doctor = jobs[5];

var Houses: cat = pets[1];
var Houses: zebra = pets[2];
var Houses: bear = pets[3];
var Houses: snails = pets[4];
var Houses: horse = pets[5];

var Houses: milk = drinks[1];
var Houses: water = drinks[2];
var Houses: tea = drinks[3];
var Houses: coffee = drinks[4];
var Houses: juice = drinks[5];

% the five houses have different colors, and their inhabitants have different
% nationalities, jobs, pets and drinks
constraint all_different(colors);
constraint all_different(nations);
constraint all_different(jobs);
constraint all_different(pets);
constraint all_different(drinks);

% the painter owns the horse
constraint painter = horse;

% the diplomat drinks coffee
constraint diplomat = coffee;

% the one who drinks milk lives in the white house
constraint white = milk;

% the Spaniard is a painter
constraint spain = painter;

% the Englishman lives in the red house
constraint england = red;

% the snails are owned by the sculptor
constraint snails = sculptor;

% the green house is immediately on the left of the red one
constraint green + 1 = red;

% the Norwegian lives immediately on the right of the blue house
constraint blue + 1 = norway;

% the doctor drinks milk
constraint doctor = milk;

% the diplomat is Japanese
constraint japan = diplomat;

% the Norwegian owns the zebra
constraint norway = zebra;

% the green house is next to the white one
constraint abs(green - white) = 1;

% the horse is owned by the neighbor of the diplomat
constraint horse = diplomat - 1 \/ horse = diplomat + 1;

% the Italian lives in the red, white or green house
constraint italy = red \/ italy = white \/ italy = green;

solve satisfy;

output ["{\"colors\": ", show(colors), ", \"nations\": ", show(nations), ", \"jobs\": ", show(jobs),
        ", \"pets\": ", show(pets), ", \"drinks\": ", show(drinks), "}"];

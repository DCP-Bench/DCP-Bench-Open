% Allergy logic puzzle: match each friend to a surname and an allergy.
% Friends are numbered Debra 0, Janet 1, Hugh 2, Rick 3.
include "globals.mzn";

var 0..3: eggs; var 0..3: mold; var 0..3: nuts; var 0..3: ragweed;
var 0..3: baxter; var 0..3: lemon; var 0..3: malone; var 0..3: fleet;

constraint all_different([eggs, mold, nuts, ragweed]);
constraint all_different([baxter, lemon, malone, fleet]);

constraint mold != 3;        % Rick is not allergic to mold
constraint eggs = baxter;
constraint lemon != 2;       % Hugh is neither Lemon nor Fleet
constraint fleet != 2;
constraint ragweed = 0;      % Debra is allergic to ragweed
constraint lemon != 1;       % Janet is not Lemon, nor eggs, nor mold
constraint eggs != 1;
constraint mold != 1;

solve satisfy;

output ["{\"eggs\": ", show(eggs), ", \"mold\": ", show(mold),
        ", \"nuts\": ", show(nuts), ", \"ragweed\": ", show(ragweed),
        ", \"baxter\": ", show(baxter), ", \"lemon\": ", show(lemon),
        ", \"malone\": ", show(malone), ", \"fleet\": ", show(fleet), "}"];

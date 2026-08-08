include "globals.mzn";

% Constants for friends
int: Debra = 0;
int: Janet = 1;
int: Hugh = 2;
int: Rick = 3;

set of int: FRIENDS = 0..3;

% Constants for allergies
int: Eggs = 0;
int: Mold = 1;
int: Nuts = 2;
int: Ragweed = 3;

set of int: ALLERGIES = 0..3;

% Constants for surnames
int: Baxter = 0;
int: Lemon = 1;
int: Malone = 2;
int: Fleet = 3;

set of int: SURNAMES = 0..3;

% Decision variables:
% allergy[f] = allergy of friend f
array[FRIENDS] of var ALLERGIES: allergy;

% surname[f] = surname of friend f
array[FRIENDS] of var SURNAMES: surname;

% Each allergy assigned to exactly one friend
constraint alldifferent(allergy);

% Each surname assigned to exactly one friend
constraint alldifferent(surname);

% Rick is not allergic to mold
constraint allergy[Rick] != Mold;

% Baxter is allergic to eggs
% Find friend with surname Baxter, that friend's allergy is eggs
constraint forall(f in FRIENDS) (
    (surname[f] = Baxter) -> (allergy[f] = Eggs)
);

% Hugh is neither surnamed Lemon nor Fleet
constraint surname[Hugh] != Lemon /\ surname[Hugh] != Fleet;

% Debra is allergic to ragweed
constraint allergy[Debra] = Ragweed;

% Janet (who isn't Lemon) is neither allergic to eggs nor to mold
constraint surname[Janet] != Lemon;
constraint allergy[Janet] != Eggs /\ allergy[Janet] != Mold;

solve satisfy;

output [
    "{",
    "\"eggs\": ", show([bool2int(allergy[f] = Eggs) | f in FRIENDS]), ",",
    "\"mold\": ", show([bool2int(allergy[f] = Mold) | f in FRIENDS]), ",",
    "\"nuts\": ", show([bool2int(allergy[f] = Nuts) | f in FRIENDS]), ",",
    "\"ragweed\": ", show([bool2int(allergy[f] = Ragweed) | f in FRIENDS]), ",",
    "\"baxter\": ", show([bool2int(surname[f] = Baxter) | f in FRIENDS]), ",",
    "\"lemon\": ", show([bool2int(surname[f] = Lemon) | f in FRIENDS]), ",",
    "\"malone\": ", show([bool2int(surname[f] = Malone) | f in FRIENDS]), ",",
    "\"fleet\": ", show([bool2int(surname[f] = Fleet) | f in FRIENDS]),
    "}"
];
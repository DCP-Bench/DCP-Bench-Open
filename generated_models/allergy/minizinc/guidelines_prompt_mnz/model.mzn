
include "globals.mzn";

% Define the set of persons
set of int: Persons = 0..3; 
% 0=Debra, 1=Janet, 2=Hugh, 3=Rick

% Define the allergies and surnames as enums
enum Allergies = {eggs, mold, nuts, ragweed};
enum Surnames  = {baxter, lemon, malone, fleet};

% Decision variables: who has which allergy and who has which surname
array[Allergies, Persons] of var bool: has_allergy;
array[Surnames, Persons] of var bool: has_surname;

% Each person has exactly one allergy; each allergy is assigned to exactly one person
constraint
  forall(p in Persons) (
    sum([bool2int(has_allergy[a,p]) | a in Allergies]) = 1
  )
  /\
  forall(a in Allergies) (
    sum([bool2int(has_allergy[a,p]) | p in Persons]) = 1
  );

% Each person has exactly one surname; each surname is assigned to exactly one person
constraint
  forall(p in Persons) (
    sum([bool2int(has_surname[s,p]) | s in Surnames]) = 1
  )
  /\
  forall(s in Surnames) (
    sum([bool2int(has_surname[s,p]) | p in Persons]) = 1
  );

% Clues:
% 1. Rick (3) is not allergic to mold
constraint has_allergy[mold, 3] = false;

% 2. Baxter is allergic to eggs (the person surnamed Baxter has eggs)
constraint
  forall(p in Persons) (
    has_surname[baxter,p] = has_allergy[eggs,p]
  );

% 3. Hugh (2) is neither surnamed Lemon nor Fleet
constraint has_surname[lemon, 2] = false /\ has_surname[fleet, 2] = false;

% 4. Debra (0) is allergic to ragweed
constraint has_allergy[ragweed, 0] = true;

% 5. Janet (1) isn't Lemon and is neither allergic to eggs nor mold
constraint
  has_surname[lemon, 1] = false
  /\ has_allergy[eggs, 1] = false
  /\ has_allergy[mold, 1] = false;

solve satisfy;

output [
  "{",
  join(",", [
    "\"eggs\": ["    ++ join(",", [show(has_allergy[eggs,p])    | p in Persons]) ++ "]",
    "\"mold\": ["    ++ join(",", [show(has_allergy[mold,p])    | p in Persons]) ++ "]",
    "\"nuts\": ["    ++ join(",", [show(has_allergy[nuts,p])    | p in Persons]) ++ "]",
    "\"ragweed\": ["++ join(",", [show(has_allergy[ragweed,p]) | p in Persons]) ++ "]",
    "\"baxter\": [" ++ join(",", [show(has_surname[baxter,p])  | p in Persons]) ++ "]",
    "\"lemon\": ["  ++ join(",", [show(has_surname[lemon,p])   | p in Persons]) ++ "]",
    "\"malone\": [" ++ join(",", [show(has_surname[malone,p])  | p in Persons]) ++ "]",
    "\"fleet\": ["  ++ join(",", [show(has_surname[fleet,p])   | p in Persons]) ++ "]"
  ]),
  "}"
];

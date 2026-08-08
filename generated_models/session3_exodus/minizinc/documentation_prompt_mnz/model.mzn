include "globals.mzn";

% We have 5 children, 5 ages, 5 countries, 5 stories
int: n = 5;

% Index sets for clarity
set of int: IDX = 1..n;

% Mapping integers to entities for clarity (not used in constraints)
% Children: Bernice=1, Carl=2, Debby=3, Sammy=4, Ted=5
% Ages: 3=1, 5=2, 7=3, 8=4, 10=5
% Countries: Ethiopia=1, Kazakhstan=2, Lithuania=3, Morocco=4, Yemen=5
% Stories: Burning bush=1, Captivity=2, Moses’s youth=3, Passover=4, Ten Commandments=5

% Decision variables:
% Each array represents a permutation of 1..5, where the position corresponds to the entity index,
% and the value corresponds to the assigned attribute index.
% For example, ages[i] = a means child i has age a.

array[IDX] of var IDX: ages;      % ages[i] = age index of child i
array[IDX] of var IDX: countries; % countries[i] = country index of child i
array[IDX] of var IDX: stories;   % stories[i] = story index of child i

% Children fixed order: Bernice=1, Carl=2, Debby=3, Sammy=4, Ted=5

% All different constraints for each attribute
constraint alldifferent(ages);
constraint alldifferent(countries);
constraint alldifferent(stories);

% 1. Debby’s family is from Lithuania.
constraint countries[3] = 3; % Debby=3, Lithuania=3

% 2. The child who told the story of the Passover is two years older than Bernice.
% Ages: 3=1,5=2,7=3,8=4,10=5
% So age index difference is 2 (e.g. Bernice age index + 2 = Passover age index)
% Find child who told Passover story: stories[i] = 4
% ages[i] = ages[Bernice] + 2
constraint
  forall(i in IDX) (
    (stories[i] = 4) -> (ages[i] = ages[1] + 2)
  );

% 3. The child whose family is from Yemen is younger than the child from the Ethiopian family.
% Yemen=5, Ethiopia=1
% ages[yemen_child] < ages[ethiopia_child]
constraint
  let {
    var IDX: yemen_child = index_set(countries, 5),
    var IDX: ethiopia_child = index_set(countries, 1)
  } in
    ages[yemen_child] < ages[ethiopia_child];

% 4. The child from the Moroccan family is three years older than Ted.
% Morocco=4, Ted=5
% ages[morocco_child] = ages[Ted] + 3
constraint
  let {
    var IDX: morocco_child = index_set(countries, 4)
  } in
    ages[morocco_child] = ages[5] + 3;

% 5. Sammy is three years older than the child who told the story of Moses’s youth in the house of the Pharaoh.
% Sammy=4, Moses’s youth=3
% ages[Sammy] = ages[moses_youth_child] + 3
constraint
  let {
    var IDX: moses_youth_child = index_set(stories, 3)
  } in
    ages[4] = ages[moses_youth_child] + 3;

% Helper function to find index of a value in an array
function var IDX: index_set(array[IDX] of var IDX: arr, int: val) =
  let {
    array[IDX] of var bool: matches = [arr[i] = val | i in IDX]
  } in
    sum(i in IDX)(i * bool2int(matches[i]));

solve satisfy;

output [
  "{",
  join(",", [
    "\"ages\": " ++ show(ages),
    "\"children\": [1,2,3,4,5]",
    "\"countries\": " ++ show(countries),
    "\"stories\": " ++ show(stories)
  ]),
  "}"
];
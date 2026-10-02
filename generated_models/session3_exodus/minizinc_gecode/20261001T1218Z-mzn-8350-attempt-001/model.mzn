% Exodus: five children (Bernice, Carl, Debby, Sammy, Ted) each present a part of
% the Exodus story, have a different age and a family from a different country.
% Find the matching of age, child, country and story from five clues.
%
% Each of the four categories is a list of five variables with values 1..5; the
% same value in two categories means the same child. Slot order in each list:
%   ages:      three, five, seven, eight, ten
%   children:  Bernice, Carl, Debby, Sammy, Ted
%   countries: Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen
%   stories:   burning bush, captivity, Moses's youth, Passover, Ten Commandments
include "globals.mzn";

int: n = 5;                         % five children in every category (fixed by the problem)

array[1..n] of var 1..n: ages;
array[1..n] of var 1..n: children;
array[1..n] of var 1..n: countries;
array[1..n] of var 1..n: stories;

% the age in years that goes with each slot of `ages` (a constant of the problem statement)
array[1..n] of int: age_years = [3, 5, 7, 8, 10];

% names for the slots of the clues
var 1..n: bernice = children[1];
var 1..n: debby = children[3];
var 1..n: sammy = children[4];
var 1..n: ted = children[5];
var 1..n: ethiopia = countries[1];
var 1..n: lithuania = countries[3];
var 1..n: morocco = countries[4];
var 1..n: yemen = countries[5];
var 1..n: moses_youth = stories[3];
var 1..n: passover = stories[4];

% every category has five different children
constraint all_different(ages);
constraint all_different(children);
constraint all_different(countries);
constraint all_different(stories);

% 1. Debby's family is from Lithuania
constraint debby = lithuania;

% In the clues below, slot i and slot j of `ages` are the two children compared;
% their years are age_years[i] and age_years[j].

% 2. the child who told the story of the Passover is two years older than Bernice
constraint forall(i, j in 1..n)
    (ages[i] = passover /\ ages[j] = bernice -> age_years[i] = age_years[j] + 2);

% 3. the child whose family is from Yemen is younger than the child from the Ethiopian family
constraint forall(i, j in 1..n)
    (ages[i] = yemen /\ ages[j] = ethiopia -> age_years[i] < age_years[j]);

% 4. the child from the Moroccan family is three years older than Ted
constraint forall(i, j in 1..n)
    (ages[i] = morocco /\ ages[j] = ted -> age_years[i] = age_years[j] + 3);

% 5. Sammy is three years older than the child who told the story of Moses's youth
constraint forall(i, j in 1..n)
    (ages[i] = sammy /\ ages[j] = moses_youth -> age_years[i] = age_years[j] + 3);

solve satisfy;

output ["{\"ages\": ", show(ages), ", \"children\": ", show(children),
        ", \"countries\": ", show(countries), ", \"stories\": ", show(stories), "}"];

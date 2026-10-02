:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% Exodus: five children (Bernice, Carl, Debby, Sammy, Ted) each present a
% different part of the Exodus story (burning bush, captivity, Moses's youth,
% Passover, Ten Commandments), each has a different age (3, 5, 7, 8, 10) and
% each family came from a different country (Ethiopia, Kazakhstan, Lithuania,
% Morocco, Yemen). Five clues link them; find the age, country and story of
% each child. The problem has no instance data; the categories are the ones in
% the statement.
%
% Every output lists its five items in the order of the statement and gives
% each item a number 1..5; the same number in two lists means the same child.
% So ages[0] is the child aged three, children[0] is Bernice, countries[0] is
% the child from Ethiopia, stories[0] is the child who told the burning bush.
model(_Instance, Vars, [ages-Ages, children-Children, countries-Countries, stories-Stories]) :-
    AgeYears = [3, 5, 7, 8, 10],   % the years of the five ages, as given in the statement

    length(Ages, 5),
    length(Children, 5),
    length(Countries, 5),
    length(Stories, 5),
    append([Ages, Children, Countries, Stories], Vars),
    Vars ins 1..5,

    % within each category the five items are different children
    maplist(all_distinct, [Ages, Children, Countries, Stories]),

    Children = [Bernice, _Carl, Debby, Sammy, Ted],
    Countries = [Ethiopia, _Kazakhstan, Lithuania, Morocco, Yemen],
    Stories = [_BurningBush, _Captivity, MosesYouth, Passover, _TenCommandments],

    % 1. Debby's family is from Lithuania.
    Debby #= Lithuania,

    % 2. The child who told the story of the Passover is two years older than
    %    Bernice.
    age_clue(Ages, AgeYears, years_older(2), Passover, Bernice),

    % 3. The child whose family is from Yemen is younger than the child from
    %    the Ethiopian family.
    age_clue(Ages, AgeYears, younger, Yemen, Ethiopia),

    % 4. The child from the Moroccan family is three years older than Ted.
    age_clue(Ages, AgeYears, years_older(3), Morocco, Ted),

    % 5. Sammy is three years older than the child who told the story of
    %    Moses's youth in the house of the Pharaoh.
    age_clue(Ages, AgeYears, years_older(3), Sammy, MosesYouth).

% age_clue(+Ages, +AgeYears, +Relation, ?ChildX, ?ChildY): the age of child X
% stands in Relation to the age of child Y. Ages[i] is the child with the
% i-th age of AgeYears. The ages are only known by their index, so the clue is
% posted as: for every pair of ages that does not satisfy Relation, X cannot
% have the first age while Y has the second.
age_clue(Ages, AgeYears, Relation, ChildX, ChildY) :-
    findall(I-J,
            ( nth1(I, AgeYears, YearsI),
              nth1(J, AgeYears, YearsJ),
              \+ call(Relation, YearsI, YearsJ) ),
            Excluded),
    maplist(exclude_age_pair(Ages, ChildX, ChildY), Excluded).

exclude_age_pair(Ages, ChildX, ChildY, I-J) :-
    nth1(I, Ages, ChildWithAgeI),
    nth1(J, Ages, ChildWithAgeJ),
    #\ (ChildWithAgeI #= ChildX #/\ ChildWithAgeJ #= ChildY).

% years_older(Gap, X, Y): the age X is Gap years more than the age Y
years_older(Gap, X, Y) :- X =:= Y + Gap.

% younger(X, Y): the age X is less than the age Y
younger(X, Y) :- X < Y.

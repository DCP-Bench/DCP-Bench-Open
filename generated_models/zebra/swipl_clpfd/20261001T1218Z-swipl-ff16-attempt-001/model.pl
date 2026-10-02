:- use_module(library(clpfd)).
:- use_module(library(apply)).

% Zebra puzzle (Einstein's puzzle): five houses stand in a row, numbered 0 to 4
% from left to right. Each house has its own colour, inhabitant nationality,
% job, pet and drink. Fourteen statements link them; find the house of every
% colour, nationality, job, pet and drink. The problem has no instance data;
% the categories and the statements are the ones in the problem text.
%
% Each output lists the items of one category in the order of the statement
% and gives the house (0..4) each item is in: colors[i] is the house of the
% i-th colour, and the same number in two lists means the same house.
model(_Instance, Vars,
      [colors-Colors, nations-Nations, jobs-Jobs, pets-Pets, drinks-Drinks]) :-
    Colors = [_Yellow, Green, Red, White, Blue],
    Nations = [Italy, Spain, Japan, England, Norway],
    Jobs = [Painter, Sculptor, Diplomat, _Pianist, Doctor],
    Pets = [_Cat, Zebra, _Bear, Snails, Horse],
    Drinks = [Milk, _Water, _Tea, Coffee, _Juice],
    append([Colors, Nations, Jobs, Pets, Drinks], Vars),
    Vars ins 0..4,

    % the five items of a category are in five different houses
    maplist(all_distinct, [Colors, Nations, Jobs, Pets, Drinks]),

    % the painter owns the horse
    Painter #= Horse,

    % the diplomat drinks coffee
    Diplomat #= Coffee,

    % the one who drinks milk lives in the white house
    White #= Milk,

    % the Spaniard is a painter
    Spain #= Painter,

    % the Englishman lives in the red house
    England #= Red,

    % the snails are owned by the sculptor
    Snails #= Sculptor,

    % the green house is immediately on the left of the red one
    Green + 1 #= Red,

    % the Norwegian lives immediately on the right of the blue house
    Blue + 1 #= Norway,

    % the doctor drinks milk
    Doctor #= Milk,

    % the diplomat is Japanese
    Japan #= Diplomat,

    % the Norwegian owns the zebra
    Norway #= Zebra,

    % the green house is next to the white one
    abs(Green - White) #= 1,

    % the horse is owned by the neighbour of the diplomat
    Horse #= Diplomat - 1 #\/ Horse #= Diplomat + 1,

    % the Italian lives in the red, white or green house
    Italy #= Red #\/ Italy #= White #\/ Italy #= Green.

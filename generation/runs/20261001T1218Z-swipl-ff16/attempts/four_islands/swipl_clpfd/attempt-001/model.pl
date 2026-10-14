:- use_module(library(clpfd)).

% Four islands: four islands (Pwana, Quero, Rayou, Skern) lie on a 2 x 2 map
% joined by bridges. Each has its own export (alabaster, bananas, coconuts,
% durian fruit) and its own tourist attraction (resort hotel, ice skating
% rink, jai alai stadium, koala preserve). Six clues say where things are;
% the task is to place every island, export and attraction on the map.
%
% The problem has no instance data. The map is part of the statement:
%
%     A -- B          positions are numbered A=0, B=1, C=2, D=3
%     |    |
%     C -- D
%
% Each of island, export and attraction lists, for each of its four items in
% the order of the statement, the map position (0..3) it sits on.
model(_Instance, Vars, [island-Island, export-Export, attraction-Attraction]) :-
    Island = [Pwana, Quero, Rayou, Skern],
    Export = [Alabaster, Bananas, _Coconuts, DurianFruit],
    Attraction = [ResortHotel, IceSkatingRink, JaiAlaiStadium, KoalaPreserve],
    append([Island, Export, Attraction], Vars),
    Vars ins 0..3,

    % each island, each export and each attraction occupies its own position
    all_distinct(Island),
    all_distinct(Export),
    all_distinct(Attraction),

    % 1. The island with the koala preserve is due south of Pwana.
    related(north_south, Pwana, KoalaPreserve),

    % 2. The island with the largest alabaster quarry is due west of Quero.
    related(west_east, Alabaster, Quero),

    % 3. The island with the resort hotel is due east of the one that exports
    %    durian fruit.
    related(west_east, DurianFruit, ResortHotel),

    % 4. Skern and the island with the jai alai stadium are connected by a
    %    north-south bridge, in either direction.
    related(north_south_bridge, Skern, JaiAlaiStadium),

    % 5. Rayou and the island that exports bananas are connected by an
    %    east-west bridge, in either direction.
    related(east_west_bridge, Rayou, Bananas),

    % 6. The islands with the ice skating rink and the jai alai stadium are
    %    not connected by a bridge. They are different islands (the attractions
    %    are all different), so they sit on diagonally opposite positions.
    related(diagonal, IceSkatingRink, JaiAlaiStadium).

% related(+Relation, ?X, ?Y): the positions X and Y stand in the map relation.
% The relations are tables over the map above, the same table the statement's
% picture gives.
related(Relation, X, Y) :-
    map_relation(Relation, Pairs),
    tuples_in([[X, Y]], Pairs).

% north_south: Y is due south of X.  west_east: Y is due east of X.
map_relation(north_south, [[0, 2], [1, 3]]).
map_relation(west_east, [[0, 1], [2, 3]]).
% bridges join neighbours; X and Y may be either end.
map_relation(north_south_bridge, [[0, 2], [2, 0], [1, 3], [3, 1]]).
map_relation(east_west_bridge, [[0, 1], [1, 0], [2, 3], [3, 2]]).
% diagonally opposite positions.
map_relation(diagonal, [[0, 3], [3, 0], [1, 2], [2, 1]]).

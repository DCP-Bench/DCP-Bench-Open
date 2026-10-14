:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(date)).

% Room assignment: give every request one room for its whole stay, so that a
% room serves one request at a time. Some requests already have a room.
model(Instance, Rooms, [room_assignments-Rooms]) :-
    MaxRooms = Instance.max_rooms,          % rooms are numbered 0..MaxRooms-1
    StartData = Instance.start_data,        % first day of each request (YYYY-MM-DD)
    EndData = Instance.end_data,            % day each request ends (the room is free that day)
    Preassigned = Instance.preassigned_room_data,   % -1: no room chosen yet
    Last is MaxRooms - 1,

    % Rooms[i] is the room given to request i. Dates become time stamps so that
    % days can be compared.
    length(StartData, NRequests),
    length(Rooms, NRequests),
    Rooms ins 0..Last,
    maplist(date_stamp, StartData, Starts),
    maplist(date_stamp, EndData, Ends),

    % some requests already have a room
    maplist([Room, Pre]>>(Pre =:= -1 -> true ; Room #= Pre), Rooms, Preassigned),

    % a room can only serve one request at a time: the requests on the same day
    % must be in different rooms. A group is looked at for the first day of each
    % request, which is enough because two requests that overlap both run on the
    % later of their first days.
    maplist({Starts, Ends, Rooms}/[Day]>>day_rooms(Day, Starts, Ends, Rooms),
            Starts).

% date_stamp(+Date, -Stamp): the time stamp of a date written as YYYY-MM-DD.
date_stamp(Date, Stamp) :-
    parse_time(Date, iso_8601, Stamp).

% day_rooms(+Day, +Starts, +Ends, +Rooms): the rooms of the requests that run on
% Day (a request runs from its first day up to, not including, its end day) are
% all different.
day_rooms(Day, Starts, Ends, Rooms) :-
    rooms_on(Day, Starts, Ends, Rooms, Group),
    (   Group = [_, _|_]
    ->  all_distinct(Group)
    ;   true
    ).

rooms_on(_, [], [], [], []).
rooms_on(Day, [Start|Starts], [End|Ends], [Room|Rooms], Group) :-
    (   Start =< Day, Day < End
    ->  Group = [Room|Group1]
    ;   Group = Group1
    ),
    rooms_on(Day, Starts, Ends, Rooms, Group1).

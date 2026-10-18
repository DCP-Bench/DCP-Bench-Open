% Room assignment problem.
% Requests with a start and an end date are each assigned to one room, for their
% entire duration, out of max_rooms rooms (0 to max_rooms - 1). Some requests are
% pre-assigned a room. A room can only serve one request at a time.

:- lib(ic).

model(Instance, Rooms, [room_assignments-Rooms]) :-
    memberchk(start_data-StartStrs, Instance),
    memberchk(end_data-EndStrs, Instance),
    memberchk(preassigned_room_data-Pre, Instance),
    memberchk(max_rooms-MaxRooms, Instance),
    ( foreach(SS, StartStrs), foreach(S, Starts) do date_key(SS, S) ),
    ( foreach(ES, EndStrs), foreach(E, Ends) do date_key(ES, E) ),
    length(Starts, N),
    length(Rooms, N),
    Rooms :: 0..MaxRooms-1,

    % Some requests may already have a room pre-assigned.
    ( foreach(R, Rooms), foreach(P, Pre) do ( P >= 0 -> R #= P ; true ) ),

    % A room can only serve one request at a time, meaning no overlapping requests
    % can be assigned to the same room. The end date is exclusive: a request that
    % checks out on the day another checks in does not overlap it.
    make_items(Starts, Ends, Rooms, Items),
    post_conflicts(Items).

% Each request as item(Start, End, Room).
make_items([], [], [], []).
make_items([S|Ss], [E|Es], [R|Rs], [item(S, E, R)|Is]) :-
    make_items(Ss, Es, Rs, Is).

% No overlapping requests share a room.
post_conflicts([]).
post_conflicts([It|Its]) :-
    post_with(It, Its),
    post_conflicts(Its).

post_with(_, []).
post_with(item(S1, E1, R1), [item(S2, E2, R2)|Its]) :-
    ( S1 < E2, S2 < E1 -> R1 #\= R2 ; true ),
    post_with(item(S1, E1, R1), Its).

% A date "YYYY-MM-DD" becomes a number that orders like the date.
date_key(DateStr, Key) :-
    string_list(DateStr, [Y1, Y2, Y3, Y4, _, M1, M2, _, D1, D2]),
    Y is (Y1 - 48) * 1000 + (Y2 - 48) * 100 + (Y3 - 48) * 10 + (Y4 - 48),
    M is (M1 - 48) * 10 + (M2 - 48),
    D is (D1 - 48) * 10 + (D2 - 48),
    Key is Y * 372 + M * 31 + D.

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

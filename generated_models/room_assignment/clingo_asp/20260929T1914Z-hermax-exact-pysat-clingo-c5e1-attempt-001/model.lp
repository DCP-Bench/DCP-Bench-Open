% Room assignment: give every booking (a request for a room from a start date
% up to, but not including, an end date) one of the rooms for its whole stay,
% so that no room hosts two bookings on the same night. Some bookings already
% have their room fixed.
% start_data(I, D), end_data(I, D): the dates of booking I as "YYYY-MM-DD" strings, which
% compare in date order; preassigned_room_data(I, R): the fixed room, or -1.
booking(I) :- start_data(I,_).

% room_assignments(I, R): booking I gets room R, from 0..max_rooms-1.
1 { room_assignments(I,R) : R = 0..M-1 } 1 :- booking(I), max_rooms(M).

% Bookings whose room is already fixed.
:- preassigned_room_data(I,R), R != -1, not room_assignments(I,R).

% Two bookings that share a night, that is, that both cover some day d with
% start <= d < end, need different rooms.
overlap(I,J) :- start_data(I,SI), end_data(I,EI), start_data(J,SJ), end_data(J,EJ), I < J,
                SI < EI, SJ < EJ, SI < EJ, SJ < EI.
:- overlap(I,J), room_assignments(I,R), room_assignments(J,R).

#show room_assignments/2.

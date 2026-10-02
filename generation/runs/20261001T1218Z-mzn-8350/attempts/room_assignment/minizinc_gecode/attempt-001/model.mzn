% Room assignment: every request (a stay with a start and an end date) is given
% one room for its whole stay. Some requests already have a room. A room can
% serve only one request at a time, so requests that overlap in time must be in
% different rooms. A request occupies its room from its start date up to, but
% not including, its end date (a guest can check in on the day another checks out).
include "globals.mzn";

int: max_rooms;                                   % rooms 0 .. max_rooms-1 are available
array[int] of string: start_data;                 % start date of each request, "YYYY-MM-DD"
array[int] of string: end_data;                   % end date of each request, "YYYY-MM-DD"
array[int] of int: preassigned_room_data;         % given room of a request, -1 if it has none

set of int: Requests = index_set(start_data);

% Dates are turned into day numbers (Julian day number of the Gregorian date),
% so that differences of day numbers are numbers of days.
array[int] of string: digit_chars = string_split("0123456789", "");
function int: digit(string: c) = min([i - 1 | i in index_set(digit_chars) where digit_chars[i] = c]);
function int: number_at(array[int] of string: chars, int: from, int: to) =
    sum(i in from..to) (digit(chars[i]) * pow(10, to - i));
function int: day_number(string: date) =
    let { array[int] of string: ch = string_split(date, "");
          int: y = number_at(ch, 1, 4);
          int: m = number_at(ch, 6, 7);
          int: d = number_at(ch, 9, 10);
          int: a = (14 - m) div 12;
          int: yy = y + 4800 - a;
          int: mm = m + 12 * a - 3 }
    in d + (153 * mm + 2) div 5 + 365 * yy + yy div 4 - yy div 100 + yy div 400 - 32045;

array[Requests] of int: first_day = [day_number(start_data[r]) | r in Requests];
array[Requests] of int: last_day_excl = [day_number(end_data[r]) | r in Requests];

% room_assignments[r] = the room request r is placed in
array[Requests] of var 0..max_rooms - 1: room_assignments;

% some requests already have a room
constraint forall(r in Requests where preassigned_room_data[r] != -1)
    (room_assignments[r] = preassigned_room_data[r]);

% A room can only serve one request at a time: the requests that are present on
% the same day must all be in different rooms. (Checked for each day from the
% first start to the last end; a request is present on days start <= day < end.)
constraint forall(day in min(first_day)..max(last_day_excl))
    (let { set of int: present = {r | r in Requests where first_day[r] <= day /\ day < last_day_excl[r]} }
     in if card(present) > 1 then all_different([room_assignments[r] | r in present]) else true endif);

solve satisfy;

output ["{\"room_assignments\": [", join(", ", [show(room_assignments[r]) | r in Requests]), "]}"];

The room assignment problem involves assigning a set of requests to a limited number of rooms such that each
request is assigned to one room for its entire duration. Some requests may already have a room pre-assigned. The main
constraint is that a room can only serve one request at a time, meaning no overlapping requests can be assigned to
the same room. A request occupies its room from its start date up to, but not including, its end date, so one request
can start in a room on the day another ends there. A pre-assigned room of -1 means that the request has none.

Print the room assignment for each request (room_assignments) as a list of integers ranging from 0 to max_rooms - 1.

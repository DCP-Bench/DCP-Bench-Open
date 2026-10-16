# room_assignment plan

- "assigning a set of requests to a limited number of rooms" -> room_assignments[i] in 0..max_rooms-1
- "each request is assigned to one room for its entire duration" -> one IntVar per request (its room); the duration is the stay from start_data to end_data
- "a room can only serve one request at a time, meaning no overlapping requests can be assigned to the same room" -> for each day that some request starts, allDifferent over the requests active that day (start <= day < end, end exclusive per the instance note)
- "Some requests may already have a room pre-assigned" -> preassigned_room_data[i] >= 0 -> room_assignments[i] = that room
- "Print the room assignment for each request (room_assignments)" -> out.put("room_assignments", rooms)
- objective: none (satisfaction)

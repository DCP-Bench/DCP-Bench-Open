The problem is to timetable a party at a yacht club. Certain boats are to be designated hosts, and the crews of the
remaining boats in turn visit the host boats for several successive half-hour periods. The crew of a host boat remains
on board to act as hosts while the crew of a guest boat together visits several hosts. Every boat can only hold a limited
number of people at a time (its capacity) and crew sizes are different. The total number of people aboard a boat,
including the host crew and guest crews, must not exceed the capacity. A guest boat cannot revisit a host and guest
crews cannot meet more than once. The problem facing the rally organizer is that of minimizing the number of host boats.

Print the visit schedule (visits) as a list of lists, where each inner list represents the boats visited - 0-based index - in each period,
e.g. visits[p,b] == v means that in period p, boat b visits boat v; a host boat's crew stays on board, so it has visits[p,b] == b, and only host boats can be visited. Also print whether each boat is a host (is_host) as a list of booleans.

# Plan: progressive party problem (csplib_013)

Problem: timetable a party. Some boats are hosts; guest crews visit hosts over several periods.

- Host boats are designated: is_host[b] -> Bool host[b].
- Each boat in each period is at one place: visits[p,b] = t -> one-hot y[p,b,t], exactly one t.
- A host stays at its own boat: y[p,h,h] <-> host[h]. Host visits are fixed to itself.
- A guest visits a host: y[p,b,t] with t != b -> host[t].
- Capacity of a host (its crew plus guest crews aboard) <= capacity: PB sum of crew_size[g] * y[p,g,h] plus crew_size[h] * host[h] <= capacity[h] per period.
- A guest boat cannot revisit a host: sum over p of y[p,g,h] <= 1 per guest g, host h.
- Guest crews cannot meet more than once: meet[p,g,g'] >= y[p,g,t] & y[p,g',t] for each t; sum over p of meet[p,g,g'] <= 1.
- Objective: minimise number of hosts: sum host[b] (minimise).
- Outputs: is_host = host, visits[p][b] = sum t * y[p,b,t].

# Plan: progressive party problem (yacht club timetabling)

Requirement (description) -> Choco constraint

- Certain boats are designated hosts (is_host[b]) -> BoolVar per boat, objective counts them.
- A host boat's crew stays on board: a host's visit in every period is itself -> for each period p and host b: is_host[b]=1 implies visits[p][b]=b.
- Guest crews visit hosts in each period: every boat's visit in each period is a host -> element(1, is_host, visits[p][b]) for every p, b.
- Each host's capacity: crew of host (if host) plus visiting guest crews <= capacity -> scalar load = crew[h]*is_host[h] + sum crew[g]*[visits[p][g]=h], load <= capacity[h] (scalar, isEq views).
- A guest boat cannot revisit a host; guest crews cannot meet more than once -> for each pair of boats i<j, number of periods they share a host (visits equal, host counts itself) <= 1 (reifyXeqY, sum <= 1). This also covers host-guest revisits.
- Minimise the number of host boats -> objective = sum(is_host) MINIMIZE.
- Outputs: visits [P][n] (0-based boat indices), is_host [n].

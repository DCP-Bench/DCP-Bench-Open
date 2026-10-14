Plan for resource-constrained project scheduling (attempt 001)

Requirement: each job has a duration and runs without interruption -> start[j] is an IntVar with domain 0..H, H = sum of durations (serial schedule bound), duration is a data constant.
Requirement: a job starts only after all its predecessors have finished (precedence pairs) -> rel(*this, start[i] + d[i] <= start[j]) per successor pair. Decomposition: no global fits a precedence list; this is the standard form.
Requirement: at every time, total use of each resource type is at most its capacity -> cumulative(*this, cap[r], start, IntArgs(dur), IntArgs(need[.][r])) per resource r, IPL default.
Requirement: the makespan is the latest finish time -> end[j] = start[j] + d[j], makespan = max(end) via max(*this, end, makespan).
Requirement: minimise the makespan -> minimize(makespan).
Output: start_time -> output("start_time", start); starts are 0-based integers.
Branching: start times first, earliest-start-first variable choice and minimum value (schedule-generation style), with Luby restarts for the optimisation search.

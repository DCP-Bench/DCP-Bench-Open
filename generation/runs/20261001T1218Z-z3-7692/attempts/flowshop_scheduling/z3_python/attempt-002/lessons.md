# Lesson: scheduling with a sequence in z3_python

attempt-001 modelled the sequence with position-by-job Booleans and an If-sum for the
processing time at each position; the 9 job, 12 machine instance timed out at 180 s. attempt-002
uses one Boolean per job pair (job i before job j), transitivity clauses, and start times per
job and machine with the disjunction "start[j] >= end[i] or start[i] >= end[j]" under that
Boolean. Processing times stay constants. All five instances were accepted, the large one in
28 s. Machine-load lower bounds on the makespan were added as implied constraints.

Requirement: the archer shoots as many arrows as she pleases at the targets; each target j has a score targets[j] per hit.
-> hits[j] IntVar with domain 0..2T/targets[j] (see bound line below), no limit on the total number of arrows

Requirement: the total score is the sum of hits times target scores.
-> total = expr(*this, sum(targets[j] * hits[j]), IPL_BND) (linear)

Requirement: bound on hits: the empty shot (no arrows) has deviation T, so an optimal total lies in 0..2T; this bounds each hits[j].
-> IntVar domains (no constraint post needed beyond the domain)

Requirement: how close the total comes to the target score (the deviation, over or under).
-> dev = expr(*this, abs(total - T)) ; the objective is dev

Requirement: the number of hits on each target is the output.
-> output("hits", hits)

Branching: over hits (decision variables), INT_VAR_SIZE_MIN, INT_VAL_SPLIT_MIN (domains are large).

Objective: minimize dev.

# Job-shop scheduling

Each job is a sequence of tasks that must run in the given order. Each task
needs one specific machine for a fixed duration, without interruption. A
machine runs at most one task at a time. Schedule every task so that the
makespan, the time at which the last task finishes, is as **small** as
possible. Time starts at 0.

Instance: `{"jobs": [[[machine, duration], ...], ...]}`; `jobs[j][k]` is task
`k` of job `j`, and machines are numbered from 0.

Print one optimal schedule as `{"start": [[s_00, s_01, ...], [s_10, ...], ...]}`,
where `s_jk` is the integer start time of task `k` of job `j`.

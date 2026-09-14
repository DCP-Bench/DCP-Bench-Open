# covering_opl
Instance: `nb_workers`, `num_tasks`, `Qualified` (1-based worker lists per task),
`Cost`. Outputs: `total_cost` (0..nb_workers*sum(Cost)) and `workers` (0/1 each).
Minimize the cost of a hired set covering every task at least once.

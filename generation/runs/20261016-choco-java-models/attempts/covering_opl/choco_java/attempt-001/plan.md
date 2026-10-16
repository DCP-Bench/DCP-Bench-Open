Select a set of workers to perform all the tasks -> one BoolVar per worker; each task is covered by its qualified workers -> m.sum(qualified workers of task, ">=", 1).post().
Each worker can perform certain tasks (Qualified, 1-based worker ids per task) -> built from the instance matrix, workers shifted to 0-based.
Hiring cost per worker (Cost) -> total_cost = m.scalar(workers, Cost, "=", total).
Objective: minimize the total hiring cost -> setObjective(MINIMIZE, total_cost).

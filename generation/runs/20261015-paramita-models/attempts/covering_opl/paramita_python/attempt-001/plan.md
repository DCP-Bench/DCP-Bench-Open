# Plan: covering_opl

Unknowns: one Bool per worker, x_i = worker i is hired (i = 1..nb_workers).

- Select a set of workers to perform all the tasks -> for each task t, Or over the workers qualified for t: Or([x_i for i in Qualified[t]]) (Bool clause, one per task)
- Ensure that all tasks are performed -> the same clause per task (covers all num_tasks tasks)
- Workers have hiring costs -> cost is the sum of Cost[i] * x_i (PB, integer weights)
- Minimise the total cost -> objective ("minimize", total_cost)
- Print total_cost and workers (list of booleans, workers[i] True if worker i is hired) -> outputs total_cost = objective expression, workers = [x_1..x_n]

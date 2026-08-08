import json

jobs_data = [
    [(0, 3), (1, 2), (2, 2)],
    [(0, 2), (2, 1), (1, 4)],
    [(1, 4), (2, 3)],
]
total_tasks = sum(len(job) for job in jobs_data)
job_ready = [0] * len(jobs_data)
machine_ready = [0] * 3
next_task = [0] * len(jobs_data)
best = None

def search(done):
    global best
    if done == total_tasks:
        makespan = max(job_ready)
        if best is None or makespan < best:
            best = makespan
        return
    if best is not None and max(job_ready) >= best:
        return
    for job_idx, tasks in enumerate(jobs_data):
        task_idx = next_task[job_idx]
        if task_idx >= len(tasks):
            continue
        machine, duration = tasks[task_idx]
        start = max(job_ready[job_idx], machine_ready[machine])
        end = start + duration
        old_job_ready = job_ready[job_idx]
        old_machine_ready = machine_ready[machine]
        next_task[job_idx] += 1
        job_ready[job_idx] = end
        machine_ready[machine] = end
        search(done + 1)
        machine_ready[machine] = old_machine_ready
        job_ready[job_idx] = old_job_ready
        next_task[job_idx] -= 1

search(0)
print(json.dumps({"makespan": best}))

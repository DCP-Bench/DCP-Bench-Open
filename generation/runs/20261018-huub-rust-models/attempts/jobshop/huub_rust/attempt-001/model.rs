// Job shop scheduling: jobs are sequences of tasks, each task runs on one specific
// machine for a given duration. Minimise the makespan (the time all jobs complete).
// Instance field jobs_data[job][task] = [machine, duration], 0-based machines.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let jobs = inst.cube("jobs_data");

    // Horizon: all tasks run one after another is always feasible.
    let mut horizon: i64 = 0;
    for job in &jobs {
        for task in job {
            horizon += task[1];
        }
    }

    // Start time of every task of every job.
    let mut start: Vec<Vec<View<i64>>> = Vec::new();
    for job in &jobs {
        let row: Vec<View<i64>> = job.iter().map(|_| m.new_int_decision(0..=horizon)).collect();
        start.push(row);
    }

    // No task for a job can be started until the previous task for that job is completed.
    for (j, job) in jobs.iter().enumerate() {
        for k in 0..job.len().saturating_sub(1) {
            let duration = job[k][1];
            m.linear(start[j][k] + duration)
                .le(start[j][k + 1])
                .post()?;
        }
    }

    // A machine can only work on one task at a time.
    // A task, once started, must run to completion.
    let machine_count = jobs
        .iter()
        .flat_map(|job| job.iter().map(|task| task[0] + 1))
        .max()
        .unwrap_or(0);
    for machine in 0..machine_count {
        let mut starts: Vec<View<i64>> = Vec::new();
        let mut durations: Vec<i64> = Vec::new();
        for (j, job) in jobs.iter().enumerate() {
            for (k, task) in job.iter().enumerate() {
                if task[0] == machine {
                    starts.push(start[j][k]);
                    durations.push(task[1]);
                }
            }
        }
        if !starts.is_empty() {
            m.disjunctive()
                .start_times(starts)
                .durations(durations)
                .post()?;
        }
    }

    // The makespan is at least the end of the last task of every job.
    let makespan = m.new_int_decision(0..=horizon);
    for (j, job) in jobs.iter().enumerate() {
        if let Some(last) = job.len().checked_sub(1) {
            m.linear(start[j][last] + job[last][1])
                .le(makespan)
                .post()?;
        }
    }

    let mut out = Out::new();
    out.put("makespan", makespan);
    out.minimise(makespan);
    Ok(out)
}

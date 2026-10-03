// Job shop: each job is a sequence of tasks, each on a given machine for a given
// duration. Tasks of a job run in order, a machine runs one task at a time, and a
// task runs to completion once started. Minimise the makespan, the time at which
// the last task ends.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    // jobs_data[job][task] = [machine, duration]. Jobs have different numbers of
    // tasks, so the field is ragged and is read from the raw JSON value.
    let jobs: Vec<Vec<(i32, i32)>> = inst
        .get("jobs_data")
        .as_array()
        .expect("jobs_data: expected an array of jobs")
        .iter()
        .map(|job| {
            job.as_array()
                .expect("jobs_data[job]: expected an array of tasks")
                .iter()
                .map(|task| {
                    let pair = task.as_array().expect("jobs_data task: expected [machine, duration]");
                    (pair[0].as_i64().unwrap() as i32, pair[1].as_i64().unwrap() as i32)
                })
                .collect()
        })
        .collect();

    // The horizon is the sum of all durations, as in the reference: running every
    // task one after another is always a valid schedule.
    let horizon: i32 = jobs.iter().flatten().map(|&(_, d)| d).sum();

    // start[j][t] and end[j][t] are the start and end times of task t of job j;
    // a task runs to completion, so end = start + duration.
    let mut start: Vec<Vec<Var>> = Vec::new();
    let mut end: Vec<Vec<Var>> = Vec::new();
    let runs = solver.new_constraint_tag();
    for job in &jobs {
        let mut s_row = Vec::new();
        let mut e_row = Vec::new();
        for &(_, duration) in job {
            let s = solver.new_bounded_integer(0, horizon);
            let e = solver.new_bounded_integer(0, horizon);
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![e.scaled(1), s.scaled(-1)], duration, runs))
                .post();
            s_row.push(s);
            e_row.push(e);
        }
        start.push(s_row);
        end.push(e_row);
    }

    // No task of a job starts before the previous task of that job has ended:
    // end[j][t-1] - start[j][t] <= 0.
    let order = solver.new_constraint_tag();
    for j in 0..jobs.len() {
        for t in 1..jobs[j].len() {
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    vec![end[j][t - 1].scaled(1), start[j][t].scaled(-1)], 0, order))
                .post();
        }
    }

    // A machine works on one task at a time: for every two tasks on the same
    // machine, one ends before the other starts. first is true when task a goes
    // first; each direction is a half-reified precedence.
    let mut machines: Vec<i32> = jobs.iter().flatten().map(|&(m, _)| m).collect();
    machines.sort();
    machines.dedup();
    let one_at_a_time = solver.new_constraint_tag();
    let resource = solver.new_constraint_tag();
    for &machine in &machines {
        let tasks: Vec<(usize, usize)> = (0..jobs.len())
            .flat_map(|j| (0..jobs[j].len()).map(move |t| (j, t)))
            .filter(|&(j, t)| jobs[j][t].0 == machine)
            .collect();
        for a in 0..tasks.len() {
            for b in (a + 1)..tasks.len() {
                let (ja, ta) = tasks[a];
                let (jb, tb) = tasks[b];
                let first = solver.new_literal();
                solver
                    .add_constraint(pumpkin_solver::less_than_or_equals(
                        vec![end[ja][ta].scaled(1), start[jb][tb].scaled(-1)], 0, one_at_a_time))
                    .implied_by(first);
                solver
                    .add_constraint(pumpkin_solver::less_than_or_equals(
                        vec![end[jb][tb].scaled(1), start[ja][ta].scaled(-1)], 0, one_at_a_time))
                    .implied_by(!first);
            }
        }
        // The same machine rule stated once more as a unit-capacity cumulative
        // over the tasks with a positive duration, so the solver also reasons
        // about the machine's total load. It adds no restriction of its own.
        let busy: Vec<(usize, usize)> = tasks
            .iter()
            .copied()
            .filter(|&(j, t)| jobs[j][t].1 > 0)
            .collect();
        if busy.len() > 1 {
            let starts: Vec<Var> = busy.iter().map(|&(j, t)| start[j][t]).collect();
            let durations: Vec<i32> = busy.iter().map(|&(j, t)| jobs[j][t].1).collect();
            let demands: Vec<i32> = vec![1; busy.len()];
            solver
                .add_constraint(pumpkin_solver::cumulative(starts, durations, demands, 1, resource))
                .post();
        }
    }

    // The makespan is the latest end time of any task.
    let makespan = solver.new_bounded_integer(0, horizon);
    let latest = solver.new_constraint_tag();
    let all_ends: Vec<Var> = end.iter().flatten().copied().collect();
    solver
        .add_constraint(pumpkin_solver::maximum(all_ends, makespan, latest))
        .post();

    let mut m = Model::new();
    m.put("makespan", makespan);
    m.minimise(makespan);
    m
}

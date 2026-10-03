// Resource-constrained project scheduling: choose start times for jobs with
// given durations so that every job starts after its predecessors finish and no
// resource is used beyond its capacity at any time, minimising the makespan.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let durations = inst.ints("durations_data");
    let needs = inst.matrix("resource_needs_data"); // needs[j][r]: job j's use of resource r
    let capacities = inst.ints("resource_capacities_data");
    let successors = inst.matrix("successors_link_data"); // [a, b]: b starts after a ends
    let n = durations.len();

    // Start times lie in 0..sum of durations, the reference's bound (all jobs one
    // after another).
    let horizon: i32 = durations.iter().sum();
    let start_time: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, horizon)).collect();

    // Precedence: a successor starts no earlier than its predecessor ends,
    // start[a] - start[b] <= -duration[a].
    let precedence = solver.new_constraint_tag();
    for link in &successors {
        let (a, b) = (link[0] as usize, link[1] as usize);
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![start_time[a].scaled(1), start_time[b].scaled(-1)], -durations[a], precedence))
            .post();
    }

    // At every moment the jobs running use at most the capacity of each
    // resource. Jobs that take no time or need none of the resource never
    // occupy it, so they are left out of that resource's cumulative.
    let resource = solver.new_constraint_tag();
    for r in 0..capacities.len() {
        let jobs: Vec<usize> = (0..n)
            .filter(|&j| durations[j] > 0 && needs[j][r] > 0)
            .collect();
        if jobs.is_empty() {
            continue;
        }
        let starts: Vec<Var> = jobs.iter().map(|&j| start_time[j]).collect();
        let lengths: Vec<i32> = jobs.iter().map(|&j| durations[j]).collect();
        let demands: Vec<i32> = jobs.iter().map(|&j| needs[j][r]).collect();
        solver
            .add_constraint(pumpkin_solver::cumulative(starts, lengths, demands, capacities[r], resource))
            .post();
    }

    // The makespan is, as in the reference, the latest start time of any job
    // (the final job is a zero-duration end marker after all others).
    let makespan = solver.new_bounded_integer(0, horizon);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::maximum(start_time.clone(), makespan, tag))
        .post();

    let mut m = Model::new();
    m.put("start_time", start_time);
    m.minimise(makespan);
    m
}

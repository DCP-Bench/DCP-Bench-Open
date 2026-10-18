// Resource-constrained project scheduling: schedule jobs with durations, resource
// requirements and precedence constraints, so that the total project duration
// (makespan) is minimised and no resource capacity is exceeded at any time.
// Output start_time: the start time of each job, one entry per job, from 0.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let durations = inst.ints("durations_data");
    let needs = inst.matrix("resource_needs_data");
    let capacities = inst.ints("resource_capacities_data");
    let links = inst.matrix("successors_link_data");
    let n = durations.len();
    let horizon: i64 = durations.iter().sum();

    // Each job starts at some time between 0 and the sum of all durations.
    let start: Vec<_> = (0..n).map(|_| m.new_int_decision(0..=horizon)).collect();
    // The makespan is the finish time of the project.
    let makespan = m.new_int_decision(0..=horizon);

    // Precedence constraints: a job can start only after its predecessors have completed.
    for link in &links {
        let p = link[0] as usize;
        let s = link[1] as usize;
        m.linear(start[p] + durations[p]).le(start[s]).post()?;
    }

    // Resource capacities: the jobs running at any time must not exceed the capacity
    // of each resource.
    for (r, capacity) in capacities.iter().enumerate() {
        let usage: Vec<i64> = needs.iter().map(|row| row[r]).collect();
        m.cumulative()
            .start_times(start.clone())
            .durations(durations.clone())
            .usages(usage)
            .capacity(*capacity)
            .post()?;
    }

    // Makespan: the project duration is at least the completion time of every job.
    for i in 0..n {
        m.linear(start[i] + durations[i]).le(makespan).post()?;
    }

    let mut out = Out::new();
    out.put("start_time", start.clone());
    out.minimise(makespan);
    Ok(out)
}

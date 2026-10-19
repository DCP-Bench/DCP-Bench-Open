// Covering OPL: select a set of workers that performs all the tasks,
// while minimizing the total hiring cost. Each worker can perform certain
// tasks and has a hiring cost. Every task must be performed.
// Qualified[t] lists the 1-based workers that can perform task t.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let nb_workers = inst.size("nb_workers");
    let cost = inst.ints("Cost");
    let qualified = inst.matrix("Qualified");

    // Whether each worker is hired.
    let hired: Vec<View<bool>> = (0..nb_workers).map(|_| m.new_bool_decision()).collect();

    // Ensure that all tasks are performed: each task needs a hired qualified worker.
    for workers in &qualified {
        let cover: Vec<View<bool>> = workers.iter().map(|&j| hired[(j - 1) as usize]).collect();
        m.linear(cover.iter().copied().sum::<IntLinearExp>()).ge(1).post()?;
    }

    // Total hiring cost of the selected workers: each worker contributes its
    // cost when hired and 0 otherwise.
    let mut contributions: Vec<View<i64>> = Vec::new();
    for (&h, &c) in hired.iter().zip(cost.iter()) {
        let z = m.new_int_decision(0..=c);
        m.linear(z).eq(c).reified_by(h).post()?;
        m.linear(z).eq(0).reified_by(!h).post()?;
        contributions.push(z);
    }
    let max_cost: i64 = cost.iter().sum();
    let total = m.new_int_decision(0..=max_cost);
    m.linear(contributions.iter().copied().sum::<IntLinearExp>()).eq(total).post()?;

    let mut out = Out::new();
    out.put("total_cost", total).put("workers", hired);
    out.minimise(total);
    Ok(out)
}

// Flow shop scheduling (permutation flow shop): jobs must be processed on
// machines 1..M in series, with the same job order on every machine. Find the
// job sequence that minimises the makespan, the time when all jobs are done.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    // pt[j][k] = processing time of job j on machine k (0-based).
    let pt = inst.matrix("process_time");
    let n = inst.len("jobs");
    let mm = inst.len("machines");
    let horizon: i64 = pt.iter().flatten().sum();

    // perm[p] is the job (0-based) placed at position p of the sequence.
    let perm = m.new_int_decisions(n, 0..=(n as i64 - 1));
    m.unique(perm.clone()).post()?;

    // The processing time of the job at position p on machine k: the job's
    // time is looked up from the column of machine k by the job at position p.
    let mut dur = Vec::with_capacity(n);
    for p in 0..n {
        let mut row = Vec::with_capacity(mm);
        for k in 0..mm {
            let col: Vec<i64> = (0..n).map(|j| pt[j][k]).collect();
            let lo = *col.iter().min().unwrap();
            let hi = *col.iter().max().unwrap();
            let d = m.new_int_decision(lo..=hi);
            m.element(col).index(perm[p]).result(d).post()?;
            row.push(d);
        }
        dur.push(row);
    }

    // Start time of the job at position p on machine k.
    let mut start = Vec::with_capacity(n);
    for _p in 0..n {
        let mut row = Vec::with_capacity(mm);
        for _k in 0..mm {
            row.push(m.new_int_decision(0..=horizon));
        }
        start.push(row);
    }

    // Each job goes to the next machine only after it has been processed on
    // the current machine: the job starts on machine k+1 once it has finished on machine k.
    for p in 0..n {
        for k in 0..mm.saturating_sub(1) {
            m.linear(start[p][k] + dur[p][k])
                .le(start[p][k + 1])
                .post()?;
        }
    }

    // Each machine processes one job at a time, in sequence order: the job at
    // position p+1 starts on a machine only after the job at position p has
    // left that machine.
    for p in 0..n.saturating_sub(1) {
        for k in 0..mm {
            m.linear(start[p][k] + dur[p][k])
                .le(start[p + 1][k])
                .post()?;
        }
    }

    // The makespan is the completion time of the last job on the last machine.
    // Every other completion time precedes it through the two chains above.
    let obj = m.new_int_decision(0..=horizon);
    if n > 0 && mm > 0 {
        m.linear(start[n - 1][mm - 1] + dur[n - 1][mm - 1])
            .le(obj)
            .post()?;
    }

    let mut out = Out::new();
    out.put("makespan", obj);
    out.minimise(obj);
    Ok(out)
}

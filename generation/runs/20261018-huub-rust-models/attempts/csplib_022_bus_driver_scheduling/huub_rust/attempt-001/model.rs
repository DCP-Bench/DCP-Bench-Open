// CSPLib prob022, bus driver scheduling: choose a subset of the given shifts so that every
// piece of work is covered by exactly one chosen shift, minimising the number of chosen shifts.
// The shifts, the number of work items and the number of shifts all come from the instance.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let num_work = inst.size("num_work");
    let num_shifts = inst.size("num_shifts");

    // shifts[s] lists the work items that shift s covers (0-based, as in the data)
    let shifts: Vec<Vec<usize>> = inst
        .get("shifts")
        .as_array()
        .expect("shifts is an array")
        .iter()
        .map(|s| {
            s.as_array()
                .expect("a shift is an array")
                .iter()
                .map(|w| w.as_u64().expect("a work index is a nonnegative integer") as usize)
                .collect()
        })
        .collect();
    assert_eq!(shifts.len(), num_shifts, "one entry of shifts per shift");

    // x[s] = 1 if shift s is selected
    let x: Vec<_> = (0..num_shifts).map(|_| m.new_bool_decision()).collect();

    // each piece of work is covered by exactly one selected shift
    for w in 0..num_work {
        let covering: Vec<_> = (0..num_shifts)
            .filter(|&s| shifts[s].contains(&w))
            .map(|s| x[s])
            .collect();
        m.linear(covering.iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
    }

    // total number of selected shifts, the objective to minimise
    let total = m.new_int_decision(0..=num_shifts as i64);
    m.linear(x.iter().copied().sum::<IntLinearExp>()).eq(total).post()?;

    let mut out = Out::new();
    out.put("x", x);
    out.minimise(total);
    Ok(out)
}

// Car selection: assign participants to cars to maximise the total number of
// assignments. Each participant is interested in a subset of the cars; each
// participant gets at most one car and each car goes to at most one participant.
// Output assignments[i][j] is true when participant i is assigned to car j.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    // The interest matrix from the instance: possible_assignments[i][j] = 1 when
    // participant i is interested in car j. Sizes come from the instance.
    let interest = inst.matrix("possible_assignments");
    let n = interest.len();
    let k = if n > 0 { interest[0].len() } else { 0 };

    // One Boolean per participant-car pair.
    let mut a: Vec<Vec<View<bool>>> = Vec::with_capacity(n);
    for _ in 0..n {
        let row: Vec<View<bool>> = (0..k).map(|_| m.new_bool_decision()).collect();
        a.push(row);
    }

    // Participants are only assigned to cars they are interested in: an
    // uninterested pair must be false.
    for i in 0..n {
        for j in 0..k {
            if interest[i][j] == 0 {
                let not_wanted = std::iter::once(a[i][j]).sum::<IntLinearExp>();
                m.linear(not_wanted).eq(0).post()?;
            }
        }
    }

    // Each participant is assigned to at most one car.
    for i in 0..n {
        let row_sum = a[i].iter().copied().sum::<IntLinearExp>();
        m.linear(row_sum).le(1).post()?;
    }

    // Each car is assigned to at most one participant.
    for j in 0..k {
        let col_sum = (0..n).map(|i| a[i][j]).sum::<IntLinearExp>();
        m.linear(col_sum).le(1).post()?;
    }

    // The objective is the total number of assignments; it is at most the
    // smaller of the two sides, since each assignment uses one participant and one car.
    let total = a.iter().flatten().copied().sum::<IntLinearExp>();
    let max_total = n.min(k) as i64;
    let obj = m.new_int_decision(0..=max_total);
    m.linear(total).eq(obj).post()?;

    let mut out = Out::new();
    out.put("assignments", a);
    out.maximise(obj);
    Ok(out)
}

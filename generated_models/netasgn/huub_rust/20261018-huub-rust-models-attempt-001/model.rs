// Project assignment problem (netasgn): people i have Supply[i] available hours, projects j
// require Demand[j] hours, and the cost per hour of person i on project j is Cost[i][j].
// Person i can contribute up to Limit[i][j] hours to project j.
// Decide the hours assign[i][j] from each person to each project, minimising the total cost.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let supply = inst.ints("supply");
    let demand = inst.ints("demand");
    let cost = inst.matrix("cost");
    let limit = inst.matrix("limit");
    let np = supply.len();
    let nq = demand.len();

    // The hours assigned from person i to project j, between 0 and Limit[i][j].
    let mut assign: Vec<Vec<View<i64>>> = Vec::with_capacity(np);
    for i in 0..np {
        let mut row = Vec::with_capacity(nq);
        for j in 0..nq {
            row.push(m.new_int_decision(0..=limit[i][j]));
        }
        assign.push(row);
    }

    // The total number of hours assigned from each person i equals its supply.
    for i in 0..np {
        m.linear(assign[i].iter().copied().sum::<IntLinearExp>())
            .eq(supply[i])
            .post()?;
    }

    // The total number of hours assigned to each project j equals its demand.
    for j in 0..nq {
        let col: Vec<View<i64>> = (0..np).map(|i| assign[i][j]).collect();
        m.linear(col.iter().copied().sum::<IntLinearExp>())
            .eq(demand[j])
            .post()?;
    }

    // The total cost is the sum of Cost[i][j] times the hours assigned from i to j.
    let mut lo: i64 = 0;
    let mut hi: i64 = 0;
    for i in 0..np {
        for j in 0..nq {
            let p = cost[i][j] * limit[i][j];
            lo += p.min(0);
            hi += p.max(0);
        }
    }
    let total = m.new_int_decision(lo..=hi);
    let weighted: Vec<View<i64>> = (0..np)
        .flat_map(|i| (0..nq).map(move |j| (i, j)))
        .map(|(i, j)| assign[i][j] * cost[i][j])
        .collect();
    m.linear(weighted.iter().copied().sum::<IntLinearExp>())
        .eq(total)
        .post()?;

    let mut out = Out::new();
    out.put("assign", assign).put("total_cost", total);
    out.minimise(total);
    Ok(out)
}

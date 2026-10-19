// csplib_010 Social golfers problem: golfers play once a week in groups of a fixed size.
// No golfer plays in the same group as any other golfer on more than one occasion.
// assign[i][j] is the group (0-based) of golfer i in week j.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n_groups = inst.size("n_groups");
    let group_size = inst.size("group_size");
    let n_weeks = inst.size("n_weeks");
    let n_golfers = n_groups * group_size;

    // The golfers each play once a week, in one of the n_groups groups.
    let mut assign: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..n_golfers {
        let mut row = Vec::new();
        for _ in 0..n_weeks {
            row.push(m.new_int_decision(0..=(n_groups as i64) - 1));
        }
        assign.push(row);
    }

    // Groups of a specific number of golfers play each week.
    for j in 0..n_weeks {
        let col: Vec<View<i64>> = (0..n_golfers).map(|i| assign[i][j]).collect();
        for g in 0..n_groups {
            m.linear(count_eq(&col, g as i64)).eq(group_size as i64).post()?;
        }
    }

    // No golfer plays in the same group as any other golfer on more than one occasion.
    for i in 0..n_golfers {
        for k in (i + 1)..n_golfers {
            let mut together = Vec::new();
            for j in 0..n_weeks {
                together.push(m.linear(assign[i][j] - assign[k][j]).eq(0).reify());
            }
            m.linear(together.iter().copied().sum::<IntLinearExp>()).le(1).post()?;
        }
    }

    let mut out = Out::new();
    out.put("assign", assign);
    Ok(out)
}

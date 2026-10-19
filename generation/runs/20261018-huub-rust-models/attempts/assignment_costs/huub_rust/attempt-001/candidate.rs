// Assignment costs: assign people to tasks with different costs, so that the total cost is minimized.
// x[i][j] is True if task i is assigned to person j.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let cost = inst.matrix("cost");
    let tasks = cost.len();
    let people = cost[0].len();

    // Each person is a 0/1 integer per task, and x[i][j] is the Boolean view xi == 1.
    let mut xi: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..tasks {
        xi.push(m.new_int_decisions(people, 0..=1));
    }

    // Each task must be assigned to exactly one person.
    for i in 0..tasks {
        m.linear(xi[i].iter().copied().sum::<IntLinearExp>()).eq(1).post()?;
    }

    // It is not necessary to assign all people to a task: each person takes at most one task.
    for j in 0..people {
        let mut col: Vec<View<i64>> = Vec::new();
        for i in 0..tasks {
            col.push(xi[i][j]);
        }
        m.linear(col.iter().copied().sum::<IntLinearExp>()).le(1).post()?;
    }

    // Minimize the total cost of the assignment.
    let mut terms: Vec<IntLinearExp> = Vec::new();
    for i in 0..tasks {
        for j in 0..people {
            terms.push((xi[i][j] * cost[i][j]).into());
        }
    }
    let total: IntLinearExp = terms.into_iter().sum();
    let lo: i64 = cost.iter().map(|r| *r.iter().min().unwrap()).sum();
    let hi: i64 = cost.iter().map(|r| *r.iter().max().unwrap()).sum();
    let obj = m.new_int_decision(lo..=hi);
    m.linear(total).eq(obj).post()?;

    let mut x: Vec<Vec<View<bool>>> = Vec::new();
    for i in 0..tasks {
        let mut row: Vec<View<bool>> = Vec::new();
        for j in 0..people {
            row.push(xi[i][j].eq(1));
        }
        x.push(row);
    }

    let mut out = Out::new();
    out.put("x", x);
    out.minimise(obj);
    Ok(out)
}

// Kidney exchange (session3_kidney_exchange): n people on a waiting list. compatible[i] is the set of
// people i can donate to. Maximise the number of people who receive a kidney: anyone who gives a kidney
// must receive one, and no person receives more than one. transplants[i][j] = 1 if person i donates to j.
// The instance lists people 1-based; the model uses 0-based indices.

// Posts that the sum of the Booleans xs equals v (as two inequalities, see the harness traps).
fn sum_eq(m: &mut Model, xs: &[View<bool>], v: View<i64>) -> Res<()> {
    m.linear(xs.iter().copied().sum::<IntLinearExp>()).le(v).post()?;
    m.linear(xs.iter().copied().sum::<IntLinearExp>()).ge(v).post()?;
    Ok(())
}

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("num_people");
    let compatible = inst.matrix("compatible");

    // transplants[i][j] is 1 if person i donates a kidney to person j.
    let mut x: Vec<Vec<View<bool>>> = Vec::new();
    for _ in 0..n {
        let mut row = Vec::new();
        for _ in 0..n {
            row.push(m.new_bool_decision());
        }
        x.push(row);
    }

    // i can donate to j only when j is in compatible[i].
    for i in 0..n {
        for j in 0..n {
            if !compatible[i].contains(&((j + 1) as i64)) {
                m.linear([x[i][j]].iter().copied().sum::<IntLinearExp>()).eq(0).post()?;
            }
        }
    }

    for i in 0..n {
        // no person receives more than one kidney: the donors to i are 0 or 1
        let received = m.new_int_decision(0..=1);
        let column: Vec<View<bool>> = (0..n).map(|r| x[r][i]).collect();
        sum_eq(m, &column, received)?;

        // no person gives more than one kidney: the recipients of i are 0 or 1
        let given = m.new_int_decision(0..=1);
        sum_eq(m, &x[i], given)?;

        // anyone who gives a kidney must receive one
        m.linear(given).le(received).post()?;
    }

    // objective: the number of kidneys transplanted, which is the number of people who receive one
    let total = m.new_int_decision(0..=(n as i64));
    let all: Vec<View<bool>> = x.iter().flatten().copied().collect();
    m.linear(all.iter().copied().sum::<IntLinearExp>()).eq(total).post()?;

    let mut out = Out::new();
    out.put("transplants", x);
    out.maximise(total);
    Ok(out)
}

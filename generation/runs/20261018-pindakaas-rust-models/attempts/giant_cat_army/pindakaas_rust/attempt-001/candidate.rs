// Giant cat army: build a list of 24 integers that starts at 0 and ends at 14.
// Each step adds 5, adds 7, or takes the square root (the result must be an integer).
// All elements are distinct, all are at most 60, and 2, 10 and 14 appear on the list in that order.
// The problem has no instance fields, so every size and bound is a fixed constant.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let len: usize = 24;
    let max: i64 = 60;
    let xs: Vec<IntVar> = (0..len).map(|_| IntVar::new(0..=max)).collect();

    // The list starts with 0.
    post(s, iv(&xs[0]), Comparator::Equal, 0)?;

    // Each step adds 5, adds 7, or takes the square root: the allowed (previous, next) pairs.
    let mut steps: Vec<Vec<i64>> = Vec::new();
    for a in 0..=max {
        if a + 5 <= max {
            steps.push(vec![a, a + 5]);
        }
        if a + 7 <= max {
            steps.push(vec![a, a + 7]);
        }
    }
    for k in 1..=max {
        if k * k <= max {
            steps.push(vec![k * k, k]);
        }
    }
    for i in 0..len - 1 {
        table(s, &[xs[i].clone(), xs[i + 1].clone()], &steps)?;
    }

    // All elements are distinct.
    all_different(s, &xs)?;

    // The list ends with 14.
    post(s, iv(&xs[len - 1]), Comparator::Equal, 14)?;

    // 2, 10 and 14 appear on the list, in that order.
    let mut twos: Vec<Lit> = Vec::new();
    let mut tens: Vec<Lit> = Vec::new();
    for x in &xs {
        twos.push(reify_eq(s, iv(x), 2)?);
        tens.push(reify_eq(s, iv(x), 10)?);
    }
    s.add_clause(twos.clone())?;
    s.add_clause(tens.clone())?;
    for j in 0..len {
        // A 10 at position j needs a 2 before it.
        let mut c: Vec<Lit> = vec![!tens[j]];
        c.extend(twos[..j].iter().cloned());
        s.add_clause(c)?;
    }

    let mut out = Out::new();
    out.put("x", &xs);
    Ok(out)
}

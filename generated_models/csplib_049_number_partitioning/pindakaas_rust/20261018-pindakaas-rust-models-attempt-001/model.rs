// csplib_049_number_partitioning: partition the numbers 1..N into two sets A and B
// (N even). Output A and B as ascending arrays of their elements, each of length N/2.

// Returns m integer variables in 1..=n, strictly ascending, whose values are exactly
// the positions i (1-based) whose literal in `lits` is true.
fn sorted_members(s: &mut Cadical, lits: &[Lit], n: i64, m: usize) -> Res<Vec<IntVar>> {
    let vs: Vec<IntVar> = (0..m).map(|_| IntVar::new(1..=n)).collect();
    for k in 1..m {
        post(s, iv(&vs[k - 1]) - iv(&vs[k]), Comparator::LessEq, -1)?;
    }
    // hits[i][k] is true when vs[k] equals i + 1
    let mut hits: Vec<Vec<Lit>> = vec![Vec::new(); lits.len()];
    for k in 0..m {
        for i in 0..lits.len() {
            let e = vs[k].equals(s, i as i64 + 1)?;
            let e = lit_of(s, e)?;
            s.add_clause([!e, lits[i]])?;
            hits[i].push(e);
        }
    }
    for i in 0..lits.len() {
        let mut clause = vec![!lits[i]];
        clause.extend(hits[i].iter().copied());
        s.add_clause(clause)?;
    }
    Ok(vs)
}

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("n");
    let half = (n / 2) as usize;

    // x[i-1] is true when the number i is in A, false when it is in B
    let xs: Vec<Lit> = (0..n).map(|_| s.new_lit()).collect();

    // A and B have the same cardinality
    let mut card = LinExp::default();
    for x in &xs {
        card += x.clone() * 2;
    }
    post(s, card, Comparator::Equal, n)?;

    // Sum of numbers in A = sum of numbers in B
    // (2 * sum over A of i = sum over 1..N of i)
    let total = n * (n + 1) / 2;
    let mut lin = LinExp::default();
    for i in 1..=n {
        lin += xs[(i - 1) as usize].clone() * (2 * i);
    }
    post(s, lin, Comparator::Equal, total)?;

    // Sum of squares of numbers in A = sum of squares of numbers in B
    // (2 * sum over A of i^2 = sum over 1..N of i^2)
    let squares_total: i64 = (1..=n).map(|i| i * i).sum();
    let mut sq = LinExp::default();
    for i in 1..=n {
        sq += xs[(i - 1) as usize].clone() * (2 * i * i);
    }
    post(s, sq, Comparator::Equal, squares_total)?;

    // Print the sets A and B.
    let a = sorted_members(s, &xs, n, half)?;
    let not_xs: Vec<Lit> = xs.iter().map(|x| !x.clone()).collect();
    let b = sorted_members(s, &not_xs, n, half)?;

    let mut out = Out::new();
    out.put("A", &a).put("B", &b);
    Ok(out)
}

// Problem csplib_003 quasigroup existence, QG3.m: an order m quasigroup (a Latin square of
// size m, each element once in every row and column) with (a*b)*(b*a) = a for all a, b.
// The output quasigroup[i][j] is i*j with values 0..m-1.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let m = inst.size("m");
    let mm = m as i64;

    // Each element occurs once in every row and column of the quasigroup.
    let mut q: Vec<Vec<IntVar>> = Vec::new();
    for _ in 0..m {
        let row: Vec<IntVar> = (0..m).map(|_| IntVar::new(0..=mm - 1)).collect();
        q.push(row);
    }
    for i in 0..m {
        all_different(s, &q[i])?;
    }
    for j in 0..m {
        let col: Vec<IntVar> = (0..m).map(|i| q[i][j].clone()).collect();
        all_different(s, &col)?;
    }

    // Each pair satisfies (a*b)*(b*a) = a. The multiplication table is flattened row-major,
    // so x*y is the element at index x*m + y.
    let flat: Vec<IntVar> = (0..m * m).map(|k| q[k / m][k % m].clone()).collect();
    for a in 0..m {
        for b in 0..m {
            // index of (a*b)*(b*a) in the flattened table: (a*b) * m + (b*a)
            let idx = define(s, scaled(&q[a][b], mm) + iv(&q[b][a]))?;
            let r = IntVar::new(0..=mm - 1);
            element_var(s, &idx, &flat, &r)?;
            post(s, iv(&r), Comparator::Equal, a as i64)?;
        }
    }

    let mut out = Out::new();
    out.put("quasigroup", &q);
    Ok(out)
}

// Problem cur_num: find a number "peculiar" between 1 and 10000 such that
// adding 1 to it gives a square number, and adding 1 to its half also gives
// a square number. The description's example 48 is excluded, since the task
// asks for another number.

// Element over a constant array, written as clauses: idx == j implies r == arr[j].
// The harness element helper builds a wide linear encoding per value and runs out
// of memory on a domain of 10^4, so the clauses are written here.
fn elem(s: &mut Cadical, idx: &IntVar, arr: &[i64], r: &IntVar) -> Res {
    for (j, &v) in arr.iter().enumerate() {
        let eq_idx = idx.equals(s, j as i64)?;
        let ij = lit_of(s, eq_idx)?;
        let eq_val = r.equals(s, v)?;
        let rv = lit_of(s, eq_val)?;
        s.add_clause([!ij, rv])?;
    }
    Ok(())
}

// A domain made of the listed values only. A plain range over 10^4 values runs out
// of memory when the harness reads the output, so wide values use holes.
fn values_domain(vals: &[i64]) -> IntVar {
    IntVar::new(dcp_pindakaas::pindakaas::RangeList::from_iter(vals.iter().map(|&v| v..=v)))
}

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // A candidate is a = 2k + 3 with k in 0..=48, so a is odd, 3 <= a <= 99,
    // and n = a*a - 1 is even and lies in 8..=9800 (within 1..=10000).
    // Peculiarity 1 holds by construction: n + 1 = a*a.
    let k = IntVar::new(0..=48);
    let ns: Vec<i64> = (0..=48i64).map(|k| (2 * k + 3) * (2 * k + 3) - 1).collect();
    let n = values_domain(&ns);
    elem(s, &k, &ns, &n)?;

    // Half of n: h = n / 2. The table gives the exact half, so n = 2h.
    let hs: Vec<i64> = ns.iter().map(|v| v / 2).collect();
    let h = values_domain(&hs);
    elem(s, &k, &hs, &h)?;

    // Peculiarity 2: h + 1 is a square number, b * b for some b in 2..=70,
    // so h = b*b - 1.
    let b = IntVar::new(2..=70);
    let squares: Vec<i64> = (2..=70i64).map(|b| b * b - 1).collect();
    let sq = values_domain(&squares);
    elem(s, &b, &squares, &sq)?;
    post(s, iv(&h) - iv(&sq), Comparator::Equal, 0)?;

    // Another number than 48: candidate a = 7 (n = 48, k = 2) is excluded.
    let eq2 = k.equals(s, 2)?;
    let is48 = lit_of(s, eq2)?;
    s.add_clause([!is48])?;

    let mut out = Out::new();
    out.put("peculiar", &n);
    Ok(out)
}

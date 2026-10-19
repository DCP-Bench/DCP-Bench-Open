// CSPLib 044: ternary Steiner problem of order n.
// Find n*(n-1)/6 triples of distinct elements from {1..n} such that any two triples
// have at most one common element. Output sets[i][j] is true when element j+1 is in
// triple i.

// The number of triples is read from the instance: m = n*(n-1)/6 rows, n columns.
fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let m = n * (n - 1) / 6;

    // sets[i][j]: element j is part of triple i.
    let b: Vec<Vec<Lit>> = (0..m)
        .map(|_| (0..n).map(|_| s.new_lit()).collect())
        .collect();

    // Each triple has exactly three distinct elements.
    for i in 0..m {
        let mut e = LinExp::default();
        for &l in &b[i] {
            e += LinExp::from(l);
        }
        post(s, e, Comparator::Equal, 3)?;
    }

    // Any two triples have at most one common element.
    // p[i][k][j] <-> (element j is in triple i and in triple k).
    for i in 0..m {
        for k in (i + 1)..m {
            let mut e = LinExp::default();
            for j in 0..n {
                let (x, y) = (b[i][j], b[k][j]);
                let p = s.new_lit();
                s.add_clause([!p, x])?;
                s.add_clause([!p, y])?;
                s.add_clause([!x, !y, p])?;
                e += LinExp::from(p);
            }
            post(s, e, Comparator::LessEq, 1)?;
        }
    }

    let mut out = Out::new();
    out.put("sets", &b);
    Ok(out)
}

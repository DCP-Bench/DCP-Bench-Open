// Problem session2_subsets_100: given a set A of distinct integers, find two disjoint
// non-empty subsets S and T of A whose element sums are equal. S and T need not cover A.
// Output in_S and in_T: for each element of A, 1 if it is in the subset, 0 otherwise.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let a = inst.ints("A");
    let n = a.len();

    // Membership literals: in_s[i] is element i in S, in_t[i] is element i in T.
    let in_s: Vec<Lit> = (0..n).map(|_| s.new_lit()).collect();
    let in_t: Vec<Lit> = (0..n).map(|_| s.new_lit()).collect();

    // S and T are disjoint: an element is in at most one of them.
    // Each element of S is not in T.
    for i in 0..n {
        s.add_clause([!in_s[i].clone(), !in_t[i].clone()])?;
    }

    // S is non-empty: at least one element is in S.
    s.add_clause(in_s.iter().cloned())?;
    // T is non-empty: at least one element is in T.
    s.add_clause(in_t.iter().cloned())?;

    // The sum of the elements in S equals the sum of the elements in T.
    let mut sum = LinExp::default();
    for i in 0..n {
        sum += LinExp::from(in_s[i].clone()) * a[i];
        sum += LinExp::from(in_t[i].clone()) * (-a[i]);
    }
    post(s, sum, Comparator::Equal, 0)?;

    let mut out = Out::new();
    out.put("in_S", &in_s).put("in_T", &in_t);
    Ok(out)
}

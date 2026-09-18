// Two disjoint non-empty subsets of A with equal sums.
fn build(inst: &Instance, cp: &mut Cp) -> Model {
    let a = inst.ints("A");
    let n = a.len();

    let in_s = cp.bools(n);
    let in_t = cp.bools(n);

    // sum(A[i] * in_S[i]) - sum(A[i] * in_T[i]) == 0
    let mut balance = weighted(&a, &in_s);
    let negated: Vec<i32> = a.iter().map(|v| -v).collect();
    balance.extend(weighted(&negated, &in_t));
    cp.eq(balance, 0);

    // disjoint: no element in both
    for i in 0..n {
        cp.at_most(&[in_s[i], in_t[i]], 1);
    }
    cp.at_least(&in_s, 1);
    cp.at_least(&in_t, 1);

    let mut m = Model::new();
    m.put("in_S", in_s);
    m.put("in_T", in_t);
    m
}

// CSPLib 044: ternary Steiner problem of order n.
// Find a set of n*(n-1)/6 triples of distinct elements of {1, ..., n} such that any two
// triples have at most one common element. Output one row per triple, one column per element.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let k = n * (n - 1) / 6;

    // The output: a k x n matrix of Booleans, row i true at column j iff element j is in triple i.
    let mut sets: Vec<Vec<View<bool>>> = Vec::new();
    for _ in 0..k {
        let mut row: Vec<View<bool>> = Vec::new();
        for _ in 0..n {
            row.push(m.new_bool_decision());
        }
        sets.push(row);
    }

    // Each triple consists of exactly three distinct elements.
    for row in &sets {
        m.linear(row.iter().copied().sum::<IntLinearExp>()).eq(3).post()?;
    }

    // Any two triples have at most one common element: two distinct triples cannot both
    // contain the same pair of elements, so for every two triples and every two elements,
    // not all four memberships hold.
    for a in 0..k {
        for b in (a + 1)..k {
            for j in 0..n {
                for l in (j + 1)..n {
                    let lits = [sets[a][j], sets[a][l], sets[b][j], sets[b][l]];
                    m.linear(lits.iter().copied().sum::<IntLinearExp>()).le(3).post()?;
                }
            }
        }
    }

    let mut out = Out::new();
    out.put("sets", sets);
    Ok(out)
}

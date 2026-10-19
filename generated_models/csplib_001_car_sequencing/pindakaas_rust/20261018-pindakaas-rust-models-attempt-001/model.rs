// Car sequencing (CSPLib 001). Cars of several types are produced in one
// sequence. Each car type is a number starting from 0. Options are installed
// at stations that can only handle a limited share of the cars passing by.
// Output: the sequence of car types on the assembly line (sequence).

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let demand = inst.ints("demand");
    let at_most = inst.ints("at_most");
    let per_slots = inst.ints("per_slots");
    let requires = inst.matrix("requires");
    let types = demand.len();
    let options = at_most.len();
    // The number of positions is the total number of cars demanded.
    let n = demand.iter().sum::<i64>() as usize;

    // Position i holds a car of type xs[i].
    let xs: Vec<IntVar> = (0..n)
        .map(|_| IntVar::new(0..=(types as i64 - 1)))
        .collect();

    // eq[i][c] <-> position i holds a car of type c.
    let mut eq: Vec<Vec<Lit>> = Vec::with_capacity(n);
    for i in 0..n {
        let mut row = Vec::with_capacity(types);
        for c in 0..types {
            row.push(reify_eq(s, iv(&xs[i]), c as i64)?);
        }
        eq.push(row);
    }

    // Each car type c is produced demand[c] times.
    for c in 0..types {
        let mut e = LinExp::default();
        for i in 0..n {
            e += LinExp::from(eq[i][c].clone());
        }
        post(s, e, Comparator::Equal, demand[c])?;
    }

    // The cars requiring a certain option must not be bunched together: in any
    // per_slots[o] consecutive positions, at most at_most[o] cars require option o.
    for o in 0..options {
        let p = per_slots[o] as usize;
        if p == 0 || p > n {
            continue;
        }
        if !(0..types).any(|c| requires[c][o] != 0) {
            continue;
        }
        for start in 0..=(n - p) {
            let mut e = LinExp::default();
            for i in start..start + p {
                for c in 0..types {
                    if requires[c][o] != 0 {
                        e += LinExp::from(eq[i][c].clone());
                    }
                }
            }
            post(s, e, Comparator::LessEq, at_most[o])?;
        }
    }

    let mut out = Out::new();
    out.put("sequence", &xs);
    Ok(out)
}

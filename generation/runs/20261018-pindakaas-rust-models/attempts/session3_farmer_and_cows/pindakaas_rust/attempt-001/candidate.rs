// Farmer and cows: cows numbered 1..num_cows, cow c gives c units of milk.
// Distribute the cows to num_sons sons so that each son gets the given number of
// cows (cows_per_son) and the same total milk.
// Output cow_assignments[c-1] is the son (0-based) of cow c.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.int("num_cows");
    let sons = inst.int("num_sons");
    let cows_per_son = inst.ints("cows_per_son");
    let total: i64 = n * (n + 1) / 2;
    let share: i64 = total / sons;

    // One variable per cow: the son it goes to.
    let mut xs: Vec<IntVar> = Vec::new();
    for _ in 0..n {
        xs.push(IntVar::new(0..=sons - 1));
    }

    // Boolean matrix b[cow][son] = (cow goes to son), as literals of the variables.
    let mut b: Vec<Vec<Lit>> = Vec::new();
    for x in &xs {
        let mut row = Vec::new();
        for son in 0..sons {
            let eq = x.equals(s, son)?;
            row.push(lit_of(s, eq)?);
        }
        b.push(row);
    }

    // Each son receives exactly cows_per_son[son] cows.
    // The number of cows is taken from the instance.
    for son in 0..sons {
        let mut e = LinExp::default();
        for c in 0..n as usize {
            e += LinExp::from(b[c][son as usize]);
        }
        post(s, e, Comparator::Equal, cows_per_son[son as usize])?;
    }

    // Each son's milk total is the same: the cow numbers add up to share.
    // Each cow contributes its own number (cow index + 1) as milk.
    for son in 0..sons {
        let mut e = LinExp::default();
        for c in 0..n as usize {
            e += LinExp::from(b[c][son as usize]) * (c as i64 + 1);
        }
        post(s, e, Comparator::Equal, share)?;
    }

    let mut out = Out::new();
    out.put("cow_assignments", &xs);
    Ok(out)
}

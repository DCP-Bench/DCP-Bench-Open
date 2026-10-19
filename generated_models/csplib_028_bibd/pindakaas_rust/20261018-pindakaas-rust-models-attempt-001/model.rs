// csplib_028_bibd: Balanced Incomplete Block Design (v, b, r, k, lambda).
// Decision: a v-by-b 0/1 incidence matrix (rows are objects, columns are blocks).
// Output "matrix": the incidence matrix, one row per object, one column per block.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let v = inst.size("v");
    let b = inst.size("b");
    let r = inst.int("r");
    let k = inst.int("k");
    let lambda = inst.int("l");

    // x[i][c] is true when object i occurs in block c.
    let mut x: Vec<Vec<Lit>> = Vec::with_capacity(v);
    for _ in 0..v {
        let mut row: Vec<Lit> = Vec::with_capacity(b);
        for _ in 0..b {
            row.push(s.new_lit());
        }
        x.push(row);
    }

    // each object occurs in exactly r different blocks
    for row in &x {
        let mut e = LinExp::default();
        for &lit in row {
            e += LinExp::from(lit);
        }
        post(s, e, Comparator::Equal, r)?;
    }

    // each block contains exactly k distinct objects
    for c in 0..b {
        let mut e = LinExp::default();
        for row in &x {
            e += LinExp::from(row[c]);
        }
        post(s, e, Comparator::Equal, k)?;
    }

    // every two distinct objects occur together in exactly lambda blocks
    for i in 0..v {
        for j in (i + 1)..v {
            let mut e = LinExp::default();
            for c in 0..b {
                // p <-> x[i][c] and x[j][c]
                let p = s.new_lit();
                let (xa, xb) = (x[i][c], x[j][c]);
                s.add_clause([!p, xa])?;
                s.add_clause([!p, xb])?;
                s.add_clause([p, !xa, !xb])?;
                e += LinExp::from(p);
            }
            post(s, e, Comparator::Equal, lambda)?;
        }
    }

    let mut out = Out::new();
    out.put("matrix", &x);
    Ok(out)
}

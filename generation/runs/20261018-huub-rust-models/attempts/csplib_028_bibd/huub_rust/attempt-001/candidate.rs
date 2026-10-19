// Balanced Incomplete Block Design (BIBD), CSPLib prob028. The output is the v by b incidence
// matrix of Booleans: rows are the v objects, columns are the b blocks.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let v = inst.size("v");
    let b = inst.size("b");
    let r = inst.int("r");
    let k = inst.int("k");
    let l = inst.int("l");

    let x: Vec<Vec<View<bool>>> = (0..v).map(|_| m.new_bool_decisions(b)).collect();

    // Each object occurs in exactly r different blocks: every row has exactly r ones.
    for i in 0..v {
        let row: Vec<View<bool>> = x[i].clone();
        m.linear(row.iter().copied().sum::<IntLinearExp>()).eq(r).post()?;
    }

    // Each block contains exactly k distinct objects: every column has exactly k ones.
    for j in 0..b {
        let col: Vec<View<bool>> = (0..v).map(|i| x[i][j]).collect();
        m.linear(col.iter().copied().sum::<IntLinearExp>()).eq(k).post()?;
    }

    // Every two distinct objects occur together in exactly lambda blocks: the scalar product
    // of any two distinct rows is lambda. Each product term is the reified conjunction of
    // the two incidences in one block.
    for i in 0..v {
        for p in (i + 1)..v {
            let mut both: Vec<View<bool>> = Vec::with_capacity(b);
            for j in 0..b {
                let z = m.proposition(BoolFormula::And(vec![
                    BoolFormula::Atom(x[i][j]),
                    BoolFormula::Atom(x[p][j]),
                ])).reify();
                both.push(z);
            }
            m.linear(both.iter().copied().sum::<IntLinearExp>()).eq(l).post()?;
        }
    }

    let mut out = Out::new();
    out.put("matrix", x);
    Ok(out)
}

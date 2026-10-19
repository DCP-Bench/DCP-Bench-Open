// Three coins lie on a table in the order given by init (1 = tails, 0 = heads).
// In precisely num_moves moves make them face either all heads or all tails.
// Each move consists of choosing one coin and flipping it over.
// Output steps[t][i]: face of coin i after t moves (true = tails), t = 0..=num_moves.
fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let init = inst.ints("init");
    let n = init.len();
    let m = inst.size("num_moves");

    // steps[t][i] is the face of coin i after t moves
    let mut steps: Vec<Vec<Lit>> = Vec::new();
    for _ in 0..=m {
        let row: Vec<Lit> = (0..n).map(|_| s.new_lit()).collect();
        steps.push(row);
    }

    // The coins lie on the table in the order tails, heads, tails at the start.
    for i in 0..n {
        let l = steps[0][i].clone();
        if init[i] == 1 {
            s.add_clause([l])?;
        } else {
            s.add_clause([!l])?;
        }
    }

    // In precisely num_moves moves, each move chooses one coin and flips it over.
    for t in 0..m {
        let flips: Vec<Lit> = (0..n).map(|_| s.new_lit()).collect();
        for i in 0..n {
            let a = steps[t][i].clone();
            let b = steps[t + 1][i].clone();
            let d = flips[i].clone();
            // d <-> a xor b
            s.add_clause([!d.clone(), a.clone(), b.clone()])?;
            s.add_clause([!d.clone(), !a.clone(), !b.clone()])?;
            s.add_clause([d.clone(), !a.clone(), b.clone()])?;
            s.add_clause([d.clone(), a.clone(), !b.clone()])?;
        }
        // choosing one coin: exactly one flip per move
        s.add_clause(flips.clone())?;
        for i in 0..n {
            for j in (i + 1)..n {
                s.add_clause([!flips[i].clone(), !flips[j].clone()])?;
            }
        }
    }

    // Make them face either all heads or all tails: all coins equal in the final state.
    for i in 1..n {
        let a = steps[m][0].clone();
        let b = steps[m][i].clone();
        s.add_clause([!a.clone(), b.clone()])?;
        s.add_clause([a, !b])?;
    }

    let mut out = Out::new();
    out.put("steps", &steps);
    Ok(out)
}

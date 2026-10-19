// Who killed Aunt Agatha? Dreadsbury Mansion is home to Agatha, the butler and Charles,
// and only them. The killer is one of the three. Output: the 0-based index of the killer.

// A grid of fresh literals: g[i][j] for residents i and j.
fn grid(s: &mut Cadical, n: usize) -> Vec<Vec<Lit>> {
    let mut g = Vec::with_capacity(n);
    for _ in 0..n {
        let mut row = Vec::with_capacity(n);
        for _ in 0..n {
            row.push(s.new_lit());
        }
        g.push(row);
    }
    g
}

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let names = inst.strings("names");
    let n = names.len();
    let find = |key: &str| names.iter().position(|nm| nm.contains(key)).expect("resident not found");
    let agatha = find("Agatha");
    let butler = find("butler");
    let charles = find("Charles");

    // hates[i][j]: resident i hates resident j. richer[i][j]: resident i is richer than resident j.
    let hates = grid(s, n);
    let richer = grid(s, n);

    // Nobody is richer than himself.
    for i in 0..n {
        s.add_clause([!richer[i][i].clone()])?;
    }

    // The killer is one of the residents: a one-hot choice of index.
    let k = IntVar::new(0..=(n as i64) - 1);
    let mut kill: Vec<Lit> = Vec::with_capacity(n);
    for i in 0..n {
        let bv = k.equals(s, i as i64)?;
        kill.push(lit_of(s, bv)?);
    }

    // A killer always hates, and is no richer than his victim (Agatha).
    for i in 0..n {
        s.add_clause([!kill[i].clone(), hates[i][agatha].clone()])?;
        s.add_clause([!kill[i].clone(), !richer[i][agatha].clone()])?;
    }

    // Agatha hates everybody except the butler.
    for x in 0..n {
        if x == butler {
            s.add_clause([!hates[agatha][x].clone()])?;
        } else {
            s.add_clause([hates[agatha][x].clone()])?;
        }
    }

    // Charles hates noone that Agatha hates.
    for x in 0..n {
        s.add_clause([!hates[agatha][x].clone(), !hates[charles][x].clone()])?;
    }

    // The butler hates everyone not richer than Aunt Agatha.
    for x in 0..n {
        s.add_clause([richer[x][agatha].clone(), hates[butler][x].clone()])?;
    }

    // The butler hates everyone whom Agatha hates.
    for x in 0..n {
        s.add_clause([!hates[agatha][x].clone(), hates[butler][x].clone()])?;
    }

    // Noone hates everyone: each resident fails to hate at least one resident.
    for x in 0..n {
        let row: Vec<Lit> = (0..n).map(|y| !hates[x][y].clone()).collect();
        s.add_clause(row)?;
    }

    let mut out = Out::new();
    out.put("killer", &k);
    Ok(out)
}

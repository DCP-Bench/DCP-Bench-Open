// Wolf, goat and cabbage river crossing: a farmer with a wolf, a goat and a
// cabbage must cross a river by boat in `stage` stages. The boat carries the
// farmer and at most one item. Left unattended together, the wolf would eat the
// goat, or the goat would eat the cabbage. Nothing may be eaten.
//
// Each entity (wolf, goat, cabbage, boat) has a shore per stage: 0 for the
// starting shore, 1 for the destination shore. Every entity is a Boolean
// decision, with a negated copy linked to it, so every clause is a sum of
// positive literals that must be at least 1.

// A Boolean decision and its negation, linked so that exactly one is 1.
fn bool_pair(m: &mut Model) -> Res<(View<bool>, View<bool>)> {
    let p = m.new_bool_decision();
    let q = m.new_bool_decision();
    eq2(m, [p, q].into_iter().sum::<IntLinearExp>(), 1)?;
    Ok((p, q))
}

// A clause: at least one of the literals holds.
fn clause(m: &mut Model, lits: &[View<bool>]) -> Res<()> {
    let sum: IntLinearExp = lits.iter().copied().sum();
    m.linear(sum).ge(1).post()?;
    Ok(())
}

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("stage");

    // Entities: 0 wolf, 1 goat, 2 cabbage, 3 boat (the farmer is with the boat).
    let mut pos: Vec<Vec<View<bool>>> = vec![Vec::new(); 4];
    let mut neg: Vec<Vec<View<bool>>> = vec![Vec::new(); 4];
    for e in 0..4 {
        for _ in 0..n {
            let (p, q) = bool_pair(m)?;
            pos[e].push(p);
            neg[e].push(q);
        }
    }

    // All start on the starting shore, and all end on the destination shore.
    for e in 0..4 {
        clause(m, &[neg[e][0]])?;
        clause(m, &[pos[e][n - 1]])?;
    }

    // If left unattended together, the wolf would eat the goat, or the goat
    // would eat the cabbage. A pair on the same shore needs the farmer there too.
    for s in 0..n {
        for (a, b) in [(0usize, 1usize), (1, 2)] {
            // a and b on the same shore (1) without the farmer (0) is forbidden.
            clause(m, &[neg[a][s], neg[b][s], pos[3][s]])?;
            // a and b on the same shore (0) without the farmer (1) is forbidden.
            clause(m, &[pos[a][s], pos[b][s], neg[3][s]])?;
        }
    }

    for s in 0..n - 1 {
        // The farmer rows the boat across at every stage: the boat changes shore.
        clause(m, &[pos[3][s], pos[3][s + 1]])?;
        clause(m, &[neg[3][s], neg[3][s + 1]])?;

        // The boat carries the farmer and a single item. An item that changes
        // shore is in the boat, so it starts on the farmer's shore.
        for e in 0..3 {
            // Item goes from shore 1 to shore 0: the farmer must be on shore 1.
            clause(m, &[neg[e][s], pos[e][s + 1], pos[3][s]])?;
            // Item goes from shore 0 to shore 1: the farmer must be on shore 0.
            clause(m, &[pos[e][s], neg[e][s + 1], neg[3][s]])?;
        }

        // The boat carries a single item: two items cannot cross in the same stage.
        for (e1, e2) in [(0usize, 1usize), (0, 2), (1, 2)] {
            // Both items and the farmer on shore 1 at stage s, all on shore 0 at s+1.
            clause(m, &[neg[e1][s], neg[e2][s], neg[3][s], pos[e1][s + 1], pos[e2][s + 1]])?;
            // Both items and the farmer on shore 0 at stage s, all on shore 1 at s+1.
            clause(m, &[pos[e1][s], pos[e2][s], pos[3][s], neg[e1][s + 1], neg[e2][s + 1]])?;
        }
    }

    let mut out = Out::new();
    out.put("wolf_pos", pos[0].clone())
        .put("goat_pos", pos[1].clone())
        .put("cabbage_pos", pos[2].clone())
        .put("boat_pos", pos[3].clone());
    Ok(out)
}

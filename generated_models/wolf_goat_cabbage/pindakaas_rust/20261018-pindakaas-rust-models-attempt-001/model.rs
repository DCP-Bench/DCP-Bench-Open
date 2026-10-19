// Wolf, goat and cabbage river crossing puzzle (satisfaction).
// A farmer with a wolf, a goat and a cabbage must cross a river by boat. The boat carries
// the farmer and at most one item. Left unattended together, the wolf eats the goat, or the
// goat eats the cabbage. Each stage gives the shore of the wolf, goat, cabbage and boat:
// 1 for the destination shore, 0 for the starting shore. The number of stages is the
// instance's stage field.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("stage");
    let mut boat: Vec<Lit> = Vec::new();
    let mut wolf: Vec<Lit> = Vec::new();
    let mut goat: Vec<Lit> = Vec::new();
    let mut cabbage: Vec<Lit> = Vec::new();
    for _ in 0..n {
        boat.push(s.new_lit());
        wolf.push(s.new_lit());
        goat.push(s.new_lit());
        cabbage.push(s.new_lit());
    }

    // Everything starts on the starting shore at the first stage.
    s.add_clause([!boat[0].clone()])?;
    s.add_clause([!wolf[0].clone()])?;
    s.add_clause([!goat[0].clone()])?;
    s.add_clause([!cabbage[0].clone()])?;

    // Everything is on the destination shore at the last stage.
    s.add_clause([boat[n - 1].clone()])?;
    s.add_clause([wolf[n - 1].clone()])?;
    s.add_clause([goat[n - 1].clone()])?;
    s.add_clause([cabbage[n - 1].clone()])?;

    // The boat alternates shores at each stage, so every stage is a crossing.
    for t in 0..n - 1 {
        s.add_clause([boat[t].clone(), boat[t + 1].clone()])?;
        s.add_clause([!boat[t].clone(), !boat[t + 1].clone()])?;
    }

    // The boat can carry only the farmer and a single item: an item that changes shore
    // must be on the boat's shore at that stage, and at most one item changes shore per crossing.
    for t in 0..n - 1 {
        let mut moves: Vec<Lit> = Vec::new();
        for x in [&wolf, &goat, &cabbage] {
            let m = s.new_lit();
            s.add_clause([!m.clone(), x[t].clone(), x[t + 1].clone()])?;
            s.add_clause([!m.clone(), !x[t].clone(), !x[t + 1].clone()])?;
            s.add_clause([m.clone(), !x[t].clone(), x[t + 1].clone()])?;
            s.add_clause([m.clone(), x[t].clone(), !x[t + 1].clone()])?;
            s.add_clause([!x[t].clone(), x[t + 1].clone(), boat[t].clone()])?;
            s.add_clause([x[t].clone(), !x[t + 1].clone(), !boat[t].clone()])?;
            moves.push(m);
        }
        for i in 0..3 {
            for j in i + 1..3 {
                s.add_clause([!moves[i].clone(), !moves[j].clone()])?;
            }
        }
    }

    // If left unattended together, the wolf eats the goat: the wolf and the goat must not share
    // a shore with the farmer on the other shore.
    for t in 0..n {
        s.add_clause([!wolf[t].clone(), !goat[t].clone(), boat[t].clone()])?;
        s.add_clause([wolf[t].clone(), goat[t].clone(), !boat[t].clone()])?;
    }

    // If left unattended together, the goat eats the cabbage: the goat and the cabbage must not
    // share a shore with the farmer on the other shore.
    for t in 0..n {
        s.add_clause([!goat[t].clone(), !cabbage[t].clone(), boat[t].clone()])?;
        s.add_clause([goat[t].clone(), cabbage[t].clone(), !boat[t].clone()])?;
    }

    let mut out = Out::new();
    out.put("boat_pos", &boat)
        .put("cabbage_pos", &cabbage)
        .put("goat_pos", &goat)
        .put("wolf_pos", &wolf);
    Ok(out)
}

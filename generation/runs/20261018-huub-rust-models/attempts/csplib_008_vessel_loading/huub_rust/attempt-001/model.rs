// csplib_008_vessel_loading: place the containers (cuboids in a single layer, parallel to the
// deck sides) on the rectangular deck without overlapping, and keep containers of classes with a
// separation apart by at least that distance along the deck or across the deck.
// Positions are printed from 0: left/top are the lower corner, right/bottom the far edge.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let dw = inst.int("deck_width");
    let dl = inst.int("deck_length");
    let w = inst.ints("width");
    let l = inst.ints("length");
    let cls = inst.ints("classes");
    let sep = inst.matrix("separation");
    let n = w.len();

    let mut xs = Vec::new();
    let mut ys = Vec::new();
    let mut ex = Vec::new();
    let mut ey = Vec::new();
    let mut lefts = Vec::new();
    let mut rights = Vec::new();
    let mut tops = Vec::new();
    let mut bottoms = Vec::new();

    // Each container takes one of its two orientations: rot = 0 keeps width along the deck width,
    // rot = 1 turns it by 90 degrees.
    for i in 0..n {
        let rot = m.new_int_decision(0..=1);
        let exi = m.element(vec![w[i], l[i]]).index(rot).define();
        let eyi = m.element(vec![l[i], w[i]]).index(rot).define();
        let x = m.new_int_decision(0..=(dw - w[i].min(l[i])).max(0));
        let y = m.new_int_decision(0..=(dl - w[i].min(l[i])).max(0));
        let r = m.new_int_decision(0..=dw);
        let b = m.new_int_decision(0..=dl);
        // The container lies inside the deck.
        m.linear(x + exi - r).eq(0).post()?;
        m.linear(y + eyi - b).eq(0).post()?;
        xs.push(x);
        ys.push(y);
        ex.push(exi);
        ey.push(eyi);
        lefts.push(x);
        rights.push(r);
        tops.push(y);
        bottoms.push(b);
    }

    // Containers do not overlap, and containers of classes with a separation are at least that
    // far apart along the deck or across the deck.
    for i in 0..n {
        for j in (i + 1)..n {
            let s = sep[(cls[i] - 1) as usize][(cls[j] - 1) as usize];
            let b1 = m.new_bool_decision();
            let b2 = m.new_bool_decision();
            let b3 = m.new_bool_decision();
            let b4 = m.new_bool_decision();
            m.linear(xs[i] + ex[i] - xs[j]).le(-s).implied_by(b1).post()?;
            m.linear(xs[j] + ex[j] - xs[i]).le(-s).implied_by(b2).post()?;
            m.linear(ys[i] + ey[i] - ys[j]).le(-s).implied_by(b3).post()?;
            m.linear(ys[j] + ey[j] - ys[i]).le(-s).implied_by(b4).post()?;
            m.proposition(
                BoolFormula::Atom(b1) | BoolFormula::Atom(b2) | BoolFormula::Atom(b3) | BoolFormula::Atom(b4),
            )
            .post()?;
        }
    }

    let mut out = Out::new();
    out.put("left", lefts)
        .put("right", rights)
        .put("top", tops)
        .put("bottom", bottoms);
    Ok(out)
}

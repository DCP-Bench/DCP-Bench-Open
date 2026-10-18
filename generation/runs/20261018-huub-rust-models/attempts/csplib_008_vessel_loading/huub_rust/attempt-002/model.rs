// csplib_008_vessel_loading: place the containers (cuboids in a single layer, positioned parallel
// to the deck sides, keeping their given width and length) on the rectangular deck without
// overlapping, and keep containers of classes with a separation apart by at least that distance
// along the deck or across the deck.
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
    let mut rights = Vec::new();
    let mut bottoms = Vec::new();

    // Each container lies inside the deck: left + width = right <= deck_width, top + length = bottom <= deck_length.
    for i in 0..n {
        let x = m.new_int_decision(0..=(dw - w[i]).max(0));
        let y = m.new_int_decision(0..=(dl - l[i]).max(0));
        let r = m.new_int_decision(0..=dw);
        let b = m.new_int_decision(0..=dl);
        m.linear(x - r).eq(-w[i]).post()?;
        m.linear(y - b).eq(-l[i]).post()?;
        xs.push(x);
        ys.push(y);
        rights.push(r);
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
            // i is left of j, j is left of i, i is below j, j is below i.
            m.linear(xs[i] - xs[j]).le(-(w[i] + s)).implied_by(b1).post()?;
            m.linear(xs[j] - xs[i]).le(-(w[j] + s)).implied_by(b2).post()?;
            m.linear(ys[i] - ys[j]).le(-(l[i] + s)).implied_by(b3).post()?;
            m.linear(ys[j] - ys[i]).le(-(l[j] + s)).implied_by(b4).post()?;
            m.proposition(
                BoolFormula::Atom(b1) | BoolFormula::Atom(b2) | BoolFormula::Atom(b3) | BoolFormula::Atom(b4),
            )
            .post()?;
        }
    }

    let mut out = Out::new();
    out.put("left", xs)
        .put("right", rights)
        .put("top", ys)
        .put("bottom", bottoms);
    Ok(out)
}

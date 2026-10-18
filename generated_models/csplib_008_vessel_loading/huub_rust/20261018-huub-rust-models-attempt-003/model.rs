// csplib_008_vessel_loading: place the containers on the rectangular deck, in one layer, parallel
// to the deck sides (so a container may be turned by 90 degrees), without overlapping, and keep
// containers of classes with a separation at least that far apart along or across the deck.
// Coordinates start from 0: left < right along the deck width, bottom < top along the deck length.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let dw = inst.int("deck_width");
    let dl = inst.int("deck_length");
    let w = inst.ints("width");
    let l = inst.ints("length");
    let cls = inst.ints("classes");
    let sep = inst.matrix("separation");
    let n = w.len();

    let mut left = Vec::new();
    let mut right = Vec::new();
    let mut bottom = Vec::new();
    let mut top = Vec::new();

    // All containers are positioned parallel to the sides of the deck and laid out in a single
    // layer: either width along the deck width and length along the deck length (rot = 0), or
    // turned by 90 degrees (rot = 1).
    for i in 0..n {
        let x0 = m.new_int_decision(0..=dw);
        let x1 = m.new_int_decision(0..=dw);
        let y0 = m.new_int_decision(0..=dl);
        let y1 = m.new_int_decision(0..=dl);
        let rot = m.new_int_decision(0..=1);
        let d = l[i] - w[i];
        // right - left = width + rot * (length - width)
        eq2(m, x1 - x0 - rot * d, w[i])?;
        // top - bottom = length - rot * (length - width)
        eq2(m, y1 - y0 + rot * d, l[i])?;
        left.push(x0);
        right.push(x1);
        bottom.push(y0);
        top.push(y1);
    }

    // The containers must not overlap, and without violating any of the separation constraints,
    // containers of classes with a minimum distance are kept that far apart along or across the deck.
    for i in 0..n {
        for j in (i + 1)..n {
            let s = sep[(cls[i] - 1) as usize][(cls[j] - 1) as usize];
            let b: Vec<_> = (0..4).map(|_| m.new_bool_decision()).collect();
            m.linear(right[i] - left[j]).le(-s).implied_by(b[0]).post()?;
            m.linear(right[j] - left[i]).le(-s).implied_by(b[1]).post()?;
            m.linear(top[i] - bottom[j]).le(-s).implied_by(b[2]).post()?;
            m.linear(top[j] - bottom[i]).le(-s).implied_by(b[3]).post()?;
            m.proposition(
                BoolFormula::Atom(b[0]) | BoolFormula::Atom(b[1]) | BoolFormula::Atom(b[2]) | BoolFormula::Atom(b[3]),
            )
            .post()?;
        }
    }

    let mut out = Out::new();
    out.put("left", left).put("right", right).put("top", top).put("bottom", bottom);
    Ok(out)
}

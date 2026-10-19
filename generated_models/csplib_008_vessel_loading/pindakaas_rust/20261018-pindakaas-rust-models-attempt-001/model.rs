// Vessel loading (csplib_008): place the containers on a rectangular deck without overlap.
// Containers are laid out in a single layer, parallel to the deck sides; each may be rotated by 90 degrees.
// Positions are 0-based: right = left + horizontal extent, top = bottom + vertical extent.
// Classes are 1-based and index the separation matrix as separation[class_i - 1][class_j - 1].

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let deck_w = inst.int("deck_width");
    let deck_l = inst.int("deck_length");
    let n = inst.size("n_containers");
    let width = inst.ints("width");
    let length = inst.ints("length");
    let classes = inst.ints("classes");
    let sep = inst.matrix("separation");

    let mut left: Vec<IntVar> = Vec::new();
    let mut right: Vec<IntVar> = Vec::new();
    let mut bottom: Vec<IntVar> = Vec::new();
    let mut top: Vec<IntVar> = Vec::new();
    let mut rot: Vec<Lit> = Vec::new();

    // Each container lies inside the deck. Its horizontal extent is its width, or its length when rotated.
    // Its vertical extent is the other one.
    for i in 0..n {
        let l = IntVar::new(0..=deck_w);
        let r = IntVar::new(0..=deck_w);
        let b = IntVar::new(0..=deck_l);
        let t = IntVar::new(0..=deck_l);
        let o = s.new_lit();
        post_if(s, &[!o.clone()], iv(&r) - iv(&l), Comparator::Equal, width[i])?;
        post_if(s, &[o.clone()], iv(&r) - iv(&l), Comparator::Equal, length[i])?;
        post_if(s, &[!o.clone()], iv(&t) - iv(&b), Comparator::Equal, length[i])?;
        post_if(s, &[o.clone()], iv(&t) - iv(&b), Comparator::Equal, width[i])?;
        left.push(l);
        right.push(r);
        bottom.push(b);
        top.push(t);
        rot.push(o);
    }

    // Containers do not overlap. Each pair of containers must be separated by the minimum distance of
    // their classes, either along the deck (left to right) or across the deck (bottom to top).
    for i in 0..n {
        for j in (i + 1)..n {
            let d = sep[(classes[i] - 1) as usize][(classes[j] - 1) as usize];
            let a = reify_le(s, iv(&right[i]) - iv(&left[j]), -d)?;
            let b = reify_le(s, iv(&right[j]) - iv(&left[i]), -d)?;
            let c = reify_le(s, iv(&top[i]) - iv(&bottom[j]), -d)?;
            let e = reify_le(s, iv(&top[j]) - iv(&bottom[i]), -d)?;
            s.add_clause([a, b, c, e])?;
        }
    }

    let mut out = Out::new();
    out.put("left", &left)
        .put("right", &right)
        .put("top", &top)
        .put("bottom", &bottom);
    Ok(out)
}

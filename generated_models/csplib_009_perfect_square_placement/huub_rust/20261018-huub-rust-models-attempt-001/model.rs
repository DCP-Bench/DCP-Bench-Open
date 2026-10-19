// csplib 009, perfect square placement: pack squares with the given integer
// sides into a bigger square of side `base`, with squares not overlapping and
// all square borders parallel to the border of the big square.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let base = inst.int("base");
    let sides = inst.ints("sides");
    let n = sides.len();

    // Each square has a lower-left corner (x, y), 0-based, with the whole
    // square inside the packing square, borders parallel to its border.
    let mut xs: Vec<View<i64>> = Vec::with_capacity(n);
    let mut ys: Vec<View<i64>> = Vec::with_capacity(n);
    for &s in &sides {
        xs.push(m.new_int_decision(0..=base - s));
        ys.push(m.new_int_decision(0..=base - s));
    }

    // The squares do not overlap each other.
    let origins: Vec<Vec<View<i64>>> = (0..n).map(|i| vec![xs[i], ys[i]]).collect();
    let sizes: Vec<Vec<View<i64>>> = sides
        .iter()
        .map(|&s| {
            let v = m.new_int_decision(s..=s);
            vec![v, v]
        })
        .collect();
    m.no_overlap().origins(origins).sizes(sizes).post()?;

    let mut out = Out::new();
    out.put("x_coords", xs).put("y_coords", ys);
    Ok(out)
}

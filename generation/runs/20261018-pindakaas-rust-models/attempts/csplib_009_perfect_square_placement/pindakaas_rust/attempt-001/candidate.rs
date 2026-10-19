// Perfect square placement (CSPLib 009): pack squares with the given integer sides
// into a square of side `base` so that no two squares overlap and all borders are
// parallel to the border of the big square. The areas sum to base^2, so there is no
// spare capacity. Output: x_coords and y_coords, the lower-left corners, 0-based.

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // The square side and the square sizes come from this instance.
    let base = inst.int("base");
    let sides = inst.ints("sides");
    let n = sides.len();

    // Pack the squares into a bigger square: each square lies inside it, 0 <= x_i and x_i + side_i <= base.
    let xs: Vec<IntVar> = sides.iter().map(|&a| IntVar::new(0..=base - a)).collect();
    let ys: Vec<IntVar> = sides.iter().map(|&a| IntVar::new(0..=base - a)).collect();

    // The squares do not overlap: for every pair, one of four separations holds.
    // The description says the squares are placed with no overlap, so every pair
    // i < j must be separated horizontally or vertically.
    for i in 0..n {
        for j in (i + 1)..n {
            let left = reify_le(s, iv(&xs[i]) - iv(&xs[j]), -sides[i])?; // x_i + s_i <= x_j
            let right = reify_le(s, iv(&xs[j]) - iv(&xs[i]), -sides[j])?; // x_j + s_j <= x_i
            let below = reify_le(s, iv(&ys[i]) - iv(&ys[j]), -sides[i])?; // y_i + s_i <= y_j
            let above = reify_le(s, iv(&ys[j]) - iv(&ys[i]), -sides[j])?; // y_j + s_j <= y_i
            s.add_clause([left, right, below, above])?;
        }
    }

    let mut out = Out::new();
    out.put("x_coords", &xs).put("y_coords", &ys);
    Ok(out)
}

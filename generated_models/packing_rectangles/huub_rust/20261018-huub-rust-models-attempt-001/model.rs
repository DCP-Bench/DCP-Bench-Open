// Packing rectangles: place the given rectangles (widths[i] x heights[i]) into a larger
// rectangle without overlap and with every rectangle inside it, minimising the area of
// the larger rectangle. Positions are 0-based; no rotation is allowed.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let widths = inst.ints("widths");
    let heights = inst.ints("heights");
    let n = widths.len();
    let sum_w: i64 = widths.iter().sum();
    let sum_h: i64 = heights.iter().sum();
    let max_w = *widths.iter().max().unwrap();
    let max_h = *heights.iter().max().unwrap();

    // Lower-left corner of each rectangle. A rectangle lies inside the box, so its
    // corner is at most the total size minus its own size; the total size is at most
    // the sum of all sizes (all rectangles side by side).
    let mut pos_x = Vec::new();
    let mut pos_y = Vec::new();
    for i in 0..n {
        pos_x.push(m.new_int_decision(0..=sum_w - widths[i]));
        pos_y.push(m.new_int_decision(0..=sum_h - heights[i]));
    }

    // total_x, total_y: width and height of the larger rectangle. The largest
    // rectangle is a lower bound on each side.
    let total_x = m.new_int_decision(max_w..=sum_w);
    let total_y = m.new_int_decision(max_h..=sum_h);

    // Objective: area = total_x * total_y.
    let area = m.new_int_decision(max_w * max_h..=sum_w * sum_h);
    m.mul(total_x, total_y).result(area).post()?;

    // Every rectangle lies within the larger rectangle:
    // pos_x[i] + widths[i] <= total_x and pos_y[i] + heights[i] <= total_y.
    for i in 0..n {
        m.linear(pos_x[i] - total_x).le(-widths[i]).post()?;
        m.linear(pos_y[i] - total_y).le(-heights[i]).post()?;
    }

    // No two rectangles overlap. For each pair (i, j), one of four separations holds:
    // i left of j, j left of i, i below j, or j below i.
    for i in 0..n {
        for j in (i + 1)..n {
            let b: Vec<_> = (0..4).map(|_| m.new_bool_decision()).collect();
            m.linear(pos_x[i] - pos_x[j]).le(-widths[i]).reified_by(b[0]).post()?;
            m.linear(pos_x[j] - pos_x[i]).le(-widths[j]).reified_by(b[1]).post()?;
            m.linear(pos_y[i] - pos_y[j]).le(-heights[i]).reified_by(b[2]).post()?;
            m.linear(pos_y[j] - pos_y[i]).le(-heights[j]).reified_by(b[3]).post()?;
            m.proposition(BoolFormula::Atom(b[0]) | BoolFormula::Atom(b[1]) | BoolFormula::Atom(b[2]) | BoolFormula::Atom(b[3])).post()?;
        }
    }

    let mut out = Out::new();
    out.put("pos_x", pos_x).put("pos_y", pos_y).put("total_x", total_x).put("total_y", total_y);
    out.minimise(area);
    Ok(out)
}

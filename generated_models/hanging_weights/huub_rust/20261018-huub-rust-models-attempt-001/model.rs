// Hanging weights puzzle: thirteen weights A-M, each an integer in 1..=13, hang
// from a system of bars. For the diagram to balance, the weights on either side
// of each pivot must be equal when weighted by their distance from the pivot, and
// a bar hanging beneath another contributes its total weight as a single weight.
// Distances are counted in units of one plus-sign (three characters) along each bar.
// The instance carries no data: the puzzle is fixed.
fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    let wa = m.new_int_decision(1..=13);
    let wb = m.new_int_decision(1..=13);
    let wc = m.new_int_decision(1..=13);
    let wd = m.new_int_decision(1..=13);
    let we = m.new_int_decision(1..=13);
    let wf = m.new_int_decision(1..=13);
    let wg = m.new_int_decision(1..=13);
    let wh = m.new_int_decision(1..=13);
    let wi = m.new_int_decision(1..=13);
    let wj = m.new_int_decision(1..=13);
    let wk = m.new_int_decision(1..=13);
    let wl = m.new_int_decision(1..=13);
    let wm = m.new_int_decision(1..=13);

    // The bar on the bottom right must have 5*C=D: C hangs five units left of
    // the pivot and D one unit right of it.
    eq2(m, wc * 5 - wd * 1, 0)?;

    // The bar above it must have 3*G=2*(C+D): G hangs three units left of its
    // pivot, and the bar C-D hangs two units right of it.
    eq2(m, wg * 3 - wc * 2 - wd * 2, 0)?;

    // The bar carrying A and B must have 4*A=B: A hangs four units left of its
    // pivot and B one unit right of it.
    eq2(m, wa * 4 - wb * 1, 0)?;

    // The bar carrying J and K, with the bars A-B and G-C-D beneath it: the
    // bar A-B hangs three units left of its pivot, J two units left, K one unit
    // right, and the bar G-C-D two units right.
    eq2(m, wa * 3 + wb * 3 + wj * 2 - wk * 1 - wg * 2 - wc * 2 - wd * 2, 0)?;

    // The bar carrying E and F must have 3*E=2*F: E hangs three units left of
    // its pivot and F two units right.
    eq2(m, we * 3 - wf * 2, 0)?;

    // The bar carrying H, I and the bar E-F: H hangs three units left of its
    // pivot, the bar E-F two units right, and I three units right.
    eq2(m, wh * 3 - we * 2 - wf * 2 - wi * 3, 0)?;

    // The bar L-M carries the bar H-I one unit left of its pivot, L one unit
    // right and M four units right.
    eq2(m, wh + we + wf + wi - wl * 1 - wm * 4, 0)?;

    // The top bar carries the bar L-M four units left of its pivot and the bar
    // J-K three units right of it.
    eq2(
        m,
        wh * 4 + we * 4 + wf * 4 + wi * 4 + wl * 4 + wm * 4
            - wa * 3 - wb * 3 - wj * 3 - wk * 3 - wg * 3 - wc * 3 - wd * 3,
        0,
    )?;

    let mut out = Out::new();
    out.put("a", wa)
        .put("b", wb)
        .put("c", wc)
        .put("d", wd)
        .put("e", we)
        .put("f", wf)
        .put("g", wg)
        .put("h", wh)
        .put("i", wi)
        .put("j", wj)
        .put("k", wk)
        .put("l", wl)
        .put("m", wm);
    Ok(out)
}

// Added corners: enter the digits 1 through 8 in the circles and squares such that the number
// in each square is equal to the sum of the numbers in the adjoining circles.
// Layout (3x3 grid, centre empty):
//   C F C
//   F   F
//   C F C
// Outputs are the eight cells in reading order: top-left, top, top-right, left, right,
// bottom-left, bottom, bottom-right.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Digits 1 through 8 in the circles and squares, each used once.
    let mut cells: Vec<View<i64>> = Vec::new();
    for _ in 0..8 {
        cells.push(m.new_int_decision(1..=8));
    }
    m.unique(cells.clone()).post()?;

    let tl = cells[0];
    let t = cells[1];
    let tr = cells[2];
    let l = cells[3];
    let r = cells[4];
    let bl = cells[5];
    let b = cells[6];
    let br = cells[7];

    // The top square is equal to the sum of the two circles adjoining it.
    m.linear(tl + tr - t).eq(0).post()?;
    // The bottom square is equal to the sum of the two circles adjoining it.
    m.linear(bl + br - b).eq(0).post()?;
    // The left square is equal to the sum of the two circles adjoining it.
    m.linear(tl + bl - l).eq(0).post()?;
    // The right square is equal to the sum of the two circles adjoining it.
    m.linear(tr + br - r).eq(0).post()?;

    let mut out = Out::new();
    out.put("positions", cells);
    Ok(out)
}

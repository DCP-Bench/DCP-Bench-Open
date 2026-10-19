// Added corners (satisfaction): enter the digits 1 through 8 in the circles and
// squares of the figure below, such that the number in each square is equal to
// the sum of the numbers in the adjoining circles. Positions are reported in
// reading order (left to right, top to bottom).
//
//   C F C
//   F   F
//   C F C
//
// p0 C, p1 F, p2 C   (top row)
// p3 F, p4 F         (middle row)
// p5 C, p6 F, p7 C   (bottom row)

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Enter the digits 1 through 8 in the circles and squares
    let p: Vec<IntVar> = (0..8).map(|_| IntVar::new(1..=8)).collect();
    all_different(s, &p)?;

    // the number in each square is equal to the sum of the numbers in the adjoining circles
    // square p1 adjoins circles p0 and p2
    post(s, iv(&p[1]) + scaled(&p[0], -1) + scaled(&p[2], -1), Comparator::Equal, 0)?;
    // square p3 adjoins circles p0 and p5
    post(s, iv(&p[3]) + scaled(&p[0], -1) + scaled(&p[5], -1), Comparator::Equal, 0)?;
    // square p4 adjoins circles p2 and p7
    post(s, iv(&p[4]) + scaled(&p[2], -1) + scaled(&p[7], -1), Comparator::Equal, 0)?;
    // square p6 adjoins circles p5 and p7
    post(s, iv(&p[6]) + scaled(&p[5], -1) + scaled(&p[7], -1), Comparator::Equal, 0)?;

    // Print the values for each position (positions), reading order
    let mut out = Out::new();
    out.put("positions", &p);
    Ok(out)
}

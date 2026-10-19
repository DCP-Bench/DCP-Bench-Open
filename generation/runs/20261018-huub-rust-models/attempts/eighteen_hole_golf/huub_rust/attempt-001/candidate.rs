// Problem: eighteen_hole_golf. Generate an 18-hole golf course where each hole
// has a length of 3, 4, or 5, and the total length of the course is 72.
// Output: the lengths of the holes (holes) as a list of 18 integers.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // each hole has a length of 3, 4, or 5
    let holes: Vec<View<i64>> = (0..18).map(|_| m.new_int_decision(3..=5)).collect();

    // the total length of the course is 72
    let total = holes.iter().copied().sum::<IntLinearExp>();
    m.linear(total).eq(72).post()?;

    let mut out = Out::new();
    out.put("holes", holes);
    Ok(out)
}

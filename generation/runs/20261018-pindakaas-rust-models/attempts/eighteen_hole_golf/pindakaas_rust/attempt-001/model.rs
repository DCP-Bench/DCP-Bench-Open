// Problem: eighteen_hole_golf. Generate a random 18-hole golf course where each
// hole has a length of 3, 4, or 5, and the total length of the course is 72.
// Output: the lengths of the holes as a list of 18 integers (holes).

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Each hole has a length of 3, 4, or 5.
    let holes: Vec<IntVar> = (0..18).map(|_| IntVar::new(3..=5)).collect();

    // The total length of the course is 72.
    let mut total = LinExp::default();
    for h in &holes {
        total += iv(h);
    }
    post(s, total, Comparator::Equal, 72)?;

    let mut out = Out::new();
    out.put("holes", &holes);
    Ok(out)
}

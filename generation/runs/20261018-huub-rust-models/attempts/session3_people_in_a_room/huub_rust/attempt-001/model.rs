// Problem session3_people_in_a_room: 13 people enter a room one at a time, 4 of them
// male and the rest female. Find an order of entry (sequence, 0 = male, 1 = female)
// so that the ratio of females to males in the room at any one time is no greater
// than 7/3. The instance has no fields; the sizes below come from the description.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    const PEOPLE: usize = 13;
    const MALES: i64 = 4;
    const FEMALES: i64 = PEOPLE as i64 - MALES;

    let seq: Vec<View<bool>> = (0..PEOPLE).map(|_| m.new_bool_decision()).collect();

    // There are 13 people. 4 of them are male.
    m.linear(seq.iter().copied().sum::<IntLinearExp>()).eq(FEMALES).post()?;

    // The ratio of females to males in the room at any one time is no greater than 7/3.
    // With f females and m males present, 3f <= 7m. Since m = k - f after k entries,
    // this is 10f <= 7k, i.e. f <= floor(7k / 10) for every prefix of length k.
    for k in 1..=PEOPLE {
        let bound = 7 * (k as i64) / 10;
        m.linear(seq[..k].iter().copied().sum::<IntLinearExp>()).le(bound).post()?;
    }

    let mut out = Out::new();
    out.put("sequence", seq);
    Ok(out)
}

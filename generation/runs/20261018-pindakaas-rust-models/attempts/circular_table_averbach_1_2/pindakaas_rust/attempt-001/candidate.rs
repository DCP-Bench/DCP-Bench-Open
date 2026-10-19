// Circular table (Averbach, Hearts): three people X, Y, Z sit around a circular table,
// seats 0, 1, 2, with 1 to the right of 0, 2 to the right of 1 and 0 to the right of 2.
// Nationalities American, English, French are held by seats 0, 1, 2.
// Each person passed three cards to the person on their right.
// Y passed three hearts to the American, so the American is on Y's right.
// X passed the queen of spades and two diamonds to the person who passed their cards to
// the Frenchwoman, so X's right-hand neighbour is the person left of the Frenchwoman.
// Determine the nationality of each person.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Seats of the three people: each is one of 0, 1, 2, and the three are distinct.
    let x = IntVar::new(0..=2);
    let y = IntVar::new(0..=2);
    let z = IntVar::new(0..=2);
    // Seats of the three nationalities.
    let american = IntVar::new(0..=2);
    let english = IntVar::new(0..=2);
    let french = IntVar::new(0..=2);

    // The three people occupy distinct seats.
    all_different(s, &[x.clone(), y.clone(), z.clone()])?;
    // The three nationalities are held by distinct people.
    all_different(s, &[american.clone(), english.clone(), french.clone()])?;

    // Y passed three hearts to the American: the American is on Y's right, seat (y + 1) mod 3.
    table(
        s,
        &[y.clone(), american.clone()],
        &vec![vec![0, 1], vec![1, 2], vec![2, 0]],
    )?;

    // X passed to the person who passed to the Frenchwoman. That person sits on X's right,
    // seat (x + 1) mod 3, and the Frenchwoman is on their right, seat (x + 2) mod 3.
    table(
        s,
        &[x.clone(), french.clone()],
        &vec![vec![0, 2], vec![1, 0], vec![2, 1]],
    )?;

    let mut out = Out::new();
    out.put("x", &x)
        .put("y", &y)
        .put("z", &z)
        .put("american", &american)
        .put("english", &english)
        .put("french", &french);
    Ok(out)
}

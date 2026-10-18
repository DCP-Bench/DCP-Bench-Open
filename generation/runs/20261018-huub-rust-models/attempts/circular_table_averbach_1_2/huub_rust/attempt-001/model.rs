// Circular table (Averbach, Hearts): three players X, Y, Z of different nationalities
// (American, English, French) sit around a circular table. Seats are 0, 1, 2 and seat 1
// is right of seat 0, seat 2 right of seat 1, and seat 0 right of seat 2.
// Each player passed three cards to the person on their right.
// x, y, z are the seats of X, Y, Z; american, english, french are the seats of the nationalities.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Seat of the person on the right of seat p (0-based, circular).
    let right: Vec<i64> = vec![1, 2, 0];

    // Seats of the three players and of the three nationalities.
    let x = m.new_int_decision(0..=2);
    let y = m.new_int_decision(0..=2);
    let z = m.new_int_decision(0..=2);
    let american = m.new_int_decision(0..=2);
    let english = m.new_int_decision(0..=2);
    let french = m.new_int_decision(0..=2);

    // Each player sits in a different seat; each nationality is held by a different seat.
    m.unique(vec![x, y, z]).post()?;
    m.unique(vec![american, english, french]).post()?;

    // Y passed three hearts to the American: the American sits on the right of Y.
    // The person on the right of Y is the American.
    m.element(right.clone()).index(y).result(american).post()?;

    // X passed the queen of spades and two diamonds to the person who passed their cards
    // to the Frenchwoman. X passes to the person on X's right, call them P. P passes to the
    // Frenchwoman, so the person on the right of P is French.
    // P = right(X), and right(P) = French.
    let p = m.new_int_decision(0..=2);
    m.element(right.clone()).index(x).result(p).post()?;
    m.element(right).index(p).result(french).post()?;

    let mut out = Out::new();
    out.put("x", x)
        .put("y", y)
        .put("z", z)
        .put("american", american)
        .put("english", english)
        .put("french", french);
    Ok(out)
}

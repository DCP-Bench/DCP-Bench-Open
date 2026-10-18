// Zebra puzzle (Einstein's puzzle), huub_rust model.
// Five houses in a row, numbered 0 to 4 from left to right. Each output lists,
// for every attribute value in the description's order, the house that has it.
// colors: yellow, green, red, white, blue
// nations: italy, spain, japan, england, norway
// pets: cat, zebra, bear, snails, horse
// drinks: milk, water, tea, coffee, juice
// jobs: painter, sculptor, diplomat, pianist, doctor

// The same house: two views take the same value.
fn same(m: &mut Model, a: View<i64>, b: View<i64>) -> Res<()> {
    eq2(m, a - b, 0)
}

// The two houses are neighbours: one is immediately left of the other.
fn next_to(m: &mut Model, a: View<i64>, b: View<i64>) -> Res<()> {
    let left = m.new_bool_decision();
    let right = m.new_bool_decision();
    m.linear(a - b).eq(1).reified_by(left).post()?;
    m.linear(b - a).eq(1).reified_by(right).post()?;
    m.proposition(BoolFormula::Atom(left) | BoolFormula::Atom(right)).post()?;
    Ok(())
}

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // There are five houses in a row, and each attribute takes each house exactly once.
    let colors = m.new_int_decisions(5, 0..=4);
    let nations = m.new_int_decisions(5, 0..=4);
    let pets = m.new_int_decisions(5, 0..=4);
    let drinks = m.new_int_decisions(5, 0..=4);
    let jobs = m.new_int_decisions(5, 0..=4);
    m.unique(colors.clone()).post()?;
    m.unique(nations.clone()).post()?;
    m.unique(pets.clone()).post()?;
    m.unique(drinks.clone()).post()?;
    m.unique(jobs.clone()).post()?;

    // The painter owns the horse.
    same(m, jobs[0], pets[4])?;
    // The diplomat drinks coffee.
    same(m, jobs[2], drinks[3])?;
    // The one who drinks milk lives in the white house.
    same(m, drinks[0], colors[3])?;
    // The Spaniard is a painter.
    same(m, nations[1], jobs[0])?;
    // The Englishman lives in the red house.
    same(m, nations[3], colors[2])?;
    // The snails are owned by the sculptor.
    same(m, pets[3], jobs[1])?;
    // The doctor drinks milk.
    same(m, jobs[4], drinks[0])?;
    // The diplomat is Japanese.
    same(m, jobs[2], nations[2])?;
    // The Norwegian owns the zebra.
    same(m, nations[4], pets[1])?;

    // The green house is immediately on the left of the red one.
    m.linear(colors[2] - colors[1]).eq(1).post()?;
    // The Norwegian lives immediately on the right of the blue house.
    m.linear(nations[4] - colors[4]).eq(1).post()?;
    // The green house is next to the white one.
    next_to(m, colors[1], colors[3])?;
    // The horse is owned by the neighbor of the diplomat.
    next_to(m, pets[4], jobs[2])?;
    // The Italian either lives in the red, white or green house.
    // The Italian is not in the yellow house and not in the blue house.
    m.linear(nations[0] - colors[0]).ne(0).post()?;
    m.linear(nations[0] - colors[4]).ne(0).post()?;

    let mut out = Out::new();
    out.put("colors", colors)
        .put("nations", nations)
        .put("pets", pets)
        .put("drinks", drinks)
        .put("jobs", jobs);
    Ok(out)
}

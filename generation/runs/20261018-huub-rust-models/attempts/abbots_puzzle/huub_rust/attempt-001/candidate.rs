// Abbot's puzzle: 100 bushels of corn are distributed among 100 people such that
// each man receives three bushels, each woman two, and each child half a bushel,
// and there are five times as many women as men. Find the number of men, women
// and children.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    let men = m.new_int_decision(0..=100);
    let women = m.new_int_decision(0..=100);
    let children = m.new_int_decision(0..=100);

    // 100 people among men, women and children.
    m.linear(men + women + children).eq(100).post()?;

    // 100 bushels: 3 per man, 2 per woman, half a bushel per child.
    // Doubled so every coefficient is an integer: 6 per man, 4 per woman, 1 per child, total 200.
    m.linear(men * 6 + women * 4 + children).eq(200).post()?;

    // There are five times as many women as men.
    m.linear(women - men * 5).le(0).post()?;
    m.linear(women - men * 5).ge(0).post()?;

    let mut out = Out::new();
    out.put("children", children).put("men", men).put("women", women);
    Ok(out)
}

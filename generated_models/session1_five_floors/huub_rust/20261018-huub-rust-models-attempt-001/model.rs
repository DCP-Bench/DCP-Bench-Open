// Five Floors (session1_five_floors): Baker, Cooper, Fletcher, Miller and Smith
// live on the first five floors of an apartment house. Find the floor of each.
// The problem has no instance data: the five people and five floors are fixed.

fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    // Each person lives on one of the floors 1 to 5.
    let baker = m.new_int_decision(1..=5);
    let cooper = m.new_int_decision(1..=5);
    let fletcher = m.new_int_decision(1..=5);
    let miller = m.new_int_decision(1..=5);
    let smith = m.new_int_decision(1..=5);

    // They all live on different floors.
    m.unique(vec![baker, cooper, fletcher, miller, smith]).post()?;

    // Baker does not live on the fifth floor.
    m.linear(baker).ne(5).post()?;

    // Cooper does not live on the first floor.
    m.linear(cooper).ne(1).post()?;

    // Fletcher does not live on either the fifth or the first floor.
    m.linear(fletcher).ne(5).post()?;
    m.linear(fletcher).ne(1).post()?;

    // Miller lives on a higher floor than does Cooper.
    m.linear(miller - cooper).ge(1).post()?;

    // Smith does not live on a floor adjacent to Fletcher's.
    // Adjacent means the floors differ by exactly 1, so the difference is neither 1 nor -1.
    m.linear(smith - fletcher).ne(1).post()?;
    m.linear(smith - fletcher).ne(-1).post()?;

    // Fletcher does not live on a floor adjacent to Cooper's.
    m.linear(fletcher - cooper).ne(1).post()?;
    m.linear(fletcher - cooper).ne(-1).post()?;

    // Print the floors where each person lives (B, C, F, M, S).
    let mut out = Out::new();
    out.put("B", baker)
        .put("C", cooper)
        .put("F", fletcher)
        .put("M", miller)
        .put("S", smith);
    Ok(out)
}

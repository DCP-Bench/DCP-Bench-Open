// Allergy puzzle: four friends (Debra = 0, Janet = 1, Hugh = 2, Rick = 3) are each
// allergic to one of eggs, mold, nuts, ragweed, and each has one of the surnames
// Baxter, Lemon, Malone, Fleet. Each food and each surname variable holds the index
// of the friend it belongs to.
fn build(_inst: &Instance, m: &mut Model) -> Res<Out> {
    let eggs = m.new_int_decision(0..=3);
    let mold = m.new_int_decision(0..=3);
    let nuts = m.new_int_decision(0..=3);
    let ragweed = m.new_int_decision(0..=3);

    let baxter = m.new_int_decision(0..=3);
    let lemon = m.new_int_decision(0..=3);
    let malone = m.new_int_decision(0..=3);
    let fleet = m.new_int_decision(0..=3);

    // Each of the four friends is allergic to something different.
    m.unique(vec![eggs, mold, nuts, ragweed]).post()?;

    // Each of the four friends has a different surname.
    m.unique(vec![baxter, lemon, malone, fleet]).post()?;

    // Rick is not allergic to mold.
    m.linear(mold).ne(3).post()?;

    // Baxter is allergic to eggs.
    eq2(m, baxter - eggs, 0)?;

    // Hugh is neither surnamed Lemon nor Fleet.
    m.linear(lemon).ne(2).post()?;
    m.linear(fleet).ne(2).post()?;

    // Debra is allergic to ragweed.
    m.linear(ragweed).eq(0).post()?;

    // Janet (who isn't Lemon) is neither allergic to eggs nor to mold.
    m.linear(lemon).ne(1).post()?;
    m.linear(eggs).ne(1).post()?;
    m.linear(mold).ne(1).post()?;

    let mut out = Out::new();
    out.put("eggs", eggs)
        .put("mold", mold)
        .put("nuts", nuts)
        .put("ragweed", ragweed)
        .put("baxter", baxter)
        .put("lemon", lemon)
        .put("malone", malone)
        .put("fleet", fleet);
    Ok(out)
}

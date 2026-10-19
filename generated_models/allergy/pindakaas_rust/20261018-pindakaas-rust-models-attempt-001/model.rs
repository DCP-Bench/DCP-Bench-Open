// Allergy puzzle: four friends (Debra = 0, Janet = 1, Hugh = 2, Rick = 3) are each
// allergic to something different (eggs, mold, nuts, ragweed) and each has a different
// surname (Baxter, Lemon, Malone, Fleet). Each output is the friend index (0..3) that
// has that allergy or that surname.

// x != c, through a literal for x == c.
fn not_equal_const(s: &mut Cadical, x: &IntVar, c: i64) -> Res {
    let b = reify_eq(s, iv(x), c)?;
    s.add_clause([!b])?;
    Ok(())
}

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let eggs = IntVar::new(0..=3);
    let mold = IntVar::new(0..=3);
    let nuts = IntVar::new(0..=3);
    let ragweed = IntVar::new(0..=3);
    let baxter = IntVar::new(0..=3);
    let lemon = IntVar::new(0..=3);
    let malone = IntVar::new(0..=3);
    let fleet = IntVar::new(0..=3);

    // each of the four friends is allergic to something different
    all_different(s, &[eggs.clone(), mold.clone(), nuts.clone(), ragweed.clone()])?;
    // each of the four friends has a different surname
    all_different(s, &[baxter.clone(), lemon.clone(), malone.clone(), fleet.clone()])?;

    // Rick is not allergic to mold
    not_equal_const(s, &mold, 3)?;
    // Baxter is allergic to eggs
    post(s, iv(&baxter) - iv(&eggs), Comparator::Equal, 0)?;
    // Hugh is neither surnamed Lemon nor Fleet
    not_equal_const(s, &lemon, 2)?;
    not_equal_const(s, &fleet, 2)?;
    // Debra is allergic to ragweed
    post(s, iv(&ragweed), Comparator::Equal, 0)?;
    // Janet (who isn't Lemon) is neither allergic to eggs nor to mold
    not_equal_const(s, &lemon, 1)?;
    not_equal_const(s, &eggs, 1)?;
    not_equal_const(s, &mold, 1)?;

    let mut out = Out::new();
    out.put("eggs", &eggs)
        .put("mold", &mold)
        .put("nuts", &nuts)
        .put("ragweed", &ragweed)
        .put("baxter", &baxter)
        .put("lemon", &lemon)
        .put("malone", &malone)
        .put("fleet", &fleet);
    Ok(out)
}

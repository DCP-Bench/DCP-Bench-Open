// Zebra puzzle (Einstein's puzzle): five houses in a row, numbered 0..4 from left to right.
// Each array gives, for each item of the category (in the order the description lists them),
// the house that item is in.

// Two entities (given as house variables) are in the same house.
fn same_house(s: &mut Cadical, a: &IntVar, b: &IntVar) -> Res {
    post(s, iv(a) - iv(b), Comparator::Equal, 0)
}

// Two entities (given as house variables) live in adjacent houses (|a - b| == 1).
fn next_to(s: &mut Cadical, a: &IntVar, b: &IntVar) -> Res {
    let d = iv(a) - iv(b);
    let plus = reify_eq(s, d.clone(), 1)?;
    let minus = reify_eq(s, d, -1)?;
    s.add_clause([plus, minus])?;
    Ok(())
}

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // The instance has no fields: the puzzle is fixed.
    let colors: Vec<IntVar> = (0..5).map(|_| IntVar::new(0..=4)).collect();
    let nations: Vec<IntVar> = (0..5).map(|_| IntVar::new(0..=4)).collect();
    let jobs: Vec<IntVar> = (0..5).map(|_| IntVar::new(0..=4)).collect();
    let pets: Vec<IntVar> = (0..5).map(|_| IntVar::new(0..=4)).collect();
    let drinks: Vec<IntVar> = (0..5).map(|_| IntVar::new(0..=4)).collect();

    // Each item of a category is in a different house.
    // colors are yellow, green, red, white, and blue
    all_different(s, &colors)?;
    // nations of inhabitants are italy, spain, japan, england, and norway
    all_different(s, &nations)?;
    // pets are cat, zebra, bear, snails, and horse
    all_different(s, &pets)?;
    // drinks are milk, water, tea, coffee, and juice
    all_different(s, &drinks)?;
    // jobs are painter, sculptor, diplomat, pianist, and doctor
    all_different(s, &jobs)?;

    // the painter owns the horse
    same_house(s, &jobs[0], &pets[4])?;
    // the diplomat drinks coffee
    same_house(s, &jobs[2], &drinks[3])?;
    // the one who drinks milk lives in the white house
    same_house(s, &drinks[0], &colors[3])?;
    // the Spaniard is a painter
    same_house(s, &nations[1], &jobs[0])?;
    // the Englishman lives in the red house
    same_house(s, &nations[3], &colors[2])?;
    // the snails are owned by the sculptor
    same_house(s, &pets[3], &jobs[1])?;
    // the green house is immediately on the left of the red one
    post(s, iv(&colors[1]) - iv(&colors[2]), Comparator::Equal, -1)?;
    // the Norwegian lives immediately on the right of the blue house
    post(s, iv(&nations[4]) - iv(&colors[4]), Comparator::Equal, 1)?;
    // the doctor drinks milk
    same_house(s, &jobs[4], &drinks[0])?;
    // the diplomat is Japanese
    same_house(s, &jobs[2], &nations[2])?;
    // the Norwegian owns the zebra
    same_house(s, &nations[4], &pets[1])?;
    // the green house is next to the white one
    next_to(s, &colors[1], &colors[3])?;
    // the horse is owned by the neighbor of the diplomat
    next_to(s, &pets[4], &jobs[2])?;
    // the Italian either lives in the red, white or green house
    let mut italian = Vec::new();
    for k in [1usize, 2, 3] {
        let d = iv(&nations[0]) - iv(&colors[k]);
        italian.push(reify_eq(s, d, 0)?);
    }
    s.add_clause(italian)?;

    let mut out = Out::new();
    out.put("colors", &colors)
        .put("drinks", &drinks)
        .put("jobs", &jobs)
        .put("nations", &nations)
        .put("pets", &pets);
    Ok(out)
}

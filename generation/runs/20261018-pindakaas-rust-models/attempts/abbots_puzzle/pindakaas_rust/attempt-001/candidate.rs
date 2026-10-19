// Abbot's puzzle (satisfaction): 100 bushels of corn are distributed among 100 people.
// Each man receives three bushels, each woman two, and each child half a bushel.
// There are five times as many women as men. Find the number of men, women and children.
// Outputs: men, women, children.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // Each count is a nonnegative integer no larger than the number of people.
    let men = IntVar::new(0..=100);
    let women = IntVar::new(0..=100);
    let children = IntVar::new(0..=100);

    // Men, women and children together make up the 100 people.
    post(s, iv(&men) + iv(&women) + iv(&children), Comparator::Equal, 100)?;
    // The 100 bushels are distributed among the 100 people.
    // Each man receives three bushels, each woman two, and each child half a bushel.
    // Doubling every amount keeps the coefficients integral: 6 per man + 4 per woman + 1 per child = 200 half-bushels.
    post(s, scaled(&men, 6) + scaled(&women, 4) + iv(&children), Comparator::Equal, 200)?;
    // There are five times as many women as men.
    post(s, iv(&women) - scaled(&men, 5), Comparator::Equal, 0)?;

    let mut out = Out::new();
    out.put("men", &men).put("women", &women).put("children", &children);
    Ok(out)
}

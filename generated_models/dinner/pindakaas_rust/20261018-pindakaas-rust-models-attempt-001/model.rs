// Dinner problem: how many grandparents (1-6), parents (1-10) and children (1-40)
// go out to dinner. Grandparents cost $3, parents $2 and children $0.50.
// Costs are kept in cents.
fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let g = IntVar::new(1..=6);
    let p = IntVar::new(1..=10);
    let c = IntVar::new(1..=40);

    // There must be 20 total people at dinner
    post(s, iv(&g) + iv(&p) + iv(&c), Comparator::Equal, 20)?;

    // and it must cost $20
    post(
        s,
        scaled(&g, 300) + scaled(&p, 200) + scaled(&c, 50),
        Comparator::Equal,
        2000,
    )?;

    let mut out = Out::new();
    out.put("grandparents", &g).put("parents", &p).put("children", &c);
    Ok(out)
}

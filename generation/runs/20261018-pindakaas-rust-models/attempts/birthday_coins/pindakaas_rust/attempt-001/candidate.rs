// birthday_coins: Tommy was given 15 coins (half-crowns, shillings and sixpence) for his
// birthday. Altogether he had 1 pound 5 shillings and 6 pence. How many half-crowns was he given?
//
// The instance carries no fields: the description fixes every value below.
// Units: a pound is 240 pence, a half-crown 30 pence, a shilling 12 pence, a sixpence 6 pence.

fn build(_inst: &Instance, s: &mut Cadical) -> Res<Out> {
    // he was given 15 coins for his birthday
    let coins = 15;
    // he found that he had 1 pound 5 shillings and 6 pence, that is 240 + 60 + 6 = 306 pence
    let total_pence = 306;

    // number of half-crowns, shillings and sixpences, each at most the number of coins
    let half_crowns = IntVar::new(0..=coins);
    let shillings = IntVar::new(0..=coins);
    let sixpences = IntVar::new(0..=coins);

    // the coins given are half-crowns, shillings and sixpence, so each kind occurs at least once
    post(s, iv(&half_crowns), Comparator::GreaterEq, 1)?;
    post(s, iv(&shillings), Comparator::GreaterEq, 1)?;
    post(s, iv(&sixpences), Comparator::GreaterEq, 1)?;

    // the 15 coins are half-crowns, shillings and sixpence together
    post(
        s,
        iv(&half_crowns) + iv(&shillings) + iv(&sixpences),
        Comparator::Equal,
        coins,
    )?;

    // the coins add up to 1 pound 5 shillings and 6 pence (306 pence)
    post(
        s,
        scaled(&half_crowns, 30) + scaled(&shillings, 12) + scaled(&sixpences, 6),
        Comparator::Equal,
        total_pence,
    )?;

    let mut out = Out::new();
    out.put("half_crowns", &half_crowns);
    Ok(out)
}

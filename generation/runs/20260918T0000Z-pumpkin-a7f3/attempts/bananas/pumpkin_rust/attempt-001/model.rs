// Buy 100 fruits for 100 dollars, with as few bananas and apples as possible.
// The prices are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let x = cp.ints(4, 1, 100);
    let (bananas, oranges, mangoes, apples) = (x[0], x[1], x[2], x[3]);

    cp.eq(terms(&x), 100);
    // 3/5 per banana, 5/7 per orange, 7/9 per mango, 9/3 per apple, all
    // multiplied through by 5*7*9 = 315 to stay integral.
    cp.eq(
        vec![
            c(3 * 189, bananas),
            c(5 * 135, oranges),
            c(7 * 105, mangoes),
            c(9 * 315, apples),
        ],
        100 * 945,
    );

    let disliked = cp.sum(vec![t(bananas), t(apples)]);

    let mut m = Model::new();
    m.put("bananas", bananas);
    m.put("oranges", oranges);
    m.put("mangoes", mangoes);
    m.put("apples", apples);
    m.minimise(disliked);
    m
}

// Twenty people at dinner for twenty dollars.
// The prices and party sizes are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let grandparents = cp.int(1, 6);
    let parents = cp.int(1, 10);
    let children = cp.int(1, 40);

    // $3, $2 and $0.50 a head, doubled to clear the half dollar.
    cp.eq(
        vec![c(6, grandparents), c(4, parents), t(children)],
        20 * 2,
    );
    cp.eq(vec![t(grandparents), t(parents), t(children)], 20);

    let mut m = Model::new();
    m.put("grandparents", grandparents);
    m.put("parents", parents);
    m.put("children", children);
    m
}

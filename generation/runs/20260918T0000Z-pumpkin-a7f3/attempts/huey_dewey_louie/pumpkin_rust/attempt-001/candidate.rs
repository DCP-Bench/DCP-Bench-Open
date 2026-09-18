// Three truthful cub scouts, and who among them is guilty.
// The statements are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, cp: &mut Cp) -> Model {
    let p = cp.bools(3);
    let (huey, dewey, louie) = (p[0], p[1], p[2]);

    // Huey: Dewey and Louie are guilty together or not at all.
    cp.same(dewey, louie);
    // Dewey: if Huey is guilty, so am I.
    cp.any(vec![!huey, dewey]);
    // Louie: Dewey and I are not both guilty.
    cp.at_most(&[dewey, louie], 1);

    let mut m = Model::new();
    m.put("huey", huey);
    m.put("dewey", dewey);
    m.put("louie", louie);
    m
}

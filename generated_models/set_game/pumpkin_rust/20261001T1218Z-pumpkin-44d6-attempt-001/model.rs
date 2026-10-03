// Set: among the cards on the table find three different cards forming a "set":
// for each of the four features (number, fill, color, shape) the three cards
// show either all the same value or three different values.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    // cards_data[c] = [number, fill, color, shape] of card c.
    let cards = inst.matrix("cards_data");
    let n = cards.len();

    // winning_cards[k] is the index of the k-th card of the set.
    let winning_cards: Vec<Var> = (0..3)
        .map(|_| solver.new_bounded_integer(0, n as i32 - 1))
        .collect();

    // The three cards are different cards.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::all_different(winning_cards.clone(), tag))
        .post();

    // For every feature the three values are all equal or all different. The
    // cards are fixed by the instance, so the triples of card indices meeting
    // this for all four features are listed here and posted as one table; the
    // table states the per-feature "all equal or all different" disjunctions
    // exactly, for every order of the three cards.
    let feature_ok = |a: i32, b: i32, c: i32| (a == b && b == c) || (a != b && b != c && a != c);
    let mut triples: Vec<Vec<i32>> = Vec::new();
    for a in 0..n {
        for b in 0..n {
            for c in 0..n {
                if a == b || b == c || a == c {
                    continue;
                }
                let features = cards[a].len();
                if (0..features).all(|f| feature_ok(cards[a][f], cards[b][f], cards[c][f])) {
                    triples.push(vec![a as i32, b as i32, c as i32]);
                }
            }
        }
    }
    let set_rule = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::table(winning_cards.clone(), triples, set_rule))
        .post();

    let mut m = Model::new();
    m.put("winning_cards", winning_cards);
    m
}

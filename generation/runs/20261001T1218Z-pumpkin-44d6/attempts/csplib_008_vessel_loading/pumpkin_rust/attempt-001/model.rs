// Vessel loading: place rectangular containers on a rectangular deck, each
// parallel to the deck sides (it may be turned by 90 degrees), without
// overlapping and keeping the minimum distances required between classes.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let deck_width = inst.int("deck_width");
    let deck_length = inst.int("deck_length");
    let n = inst.size("n_containers");
    let width = inst.ints("width"); // width of each container
    let length = inst.ints("length"); // length of each container
    let classes = inst.ints("classes"); // class of each container, counted from 1
    let separation = inst.matrix("separation"); // minimum distance between two classes

    // Container i occupies columns left[i]..right[i] along the deck width and
    // rows bottom[i]..top[i] along the deck length, inside the deck.
    let left: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, deck_width)).collect();
    let right: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, deck_width)).collect();
    let top: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, deck_length)).collect();
    let bottom: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, deck_length)).collect();

    // Shape of each container: either it lies as given (extent width[i] across
    // the deck, length[i] along it) or turned (length[i] across, width[i] along).
    // turned[i] picks the case; each case is half-reified on it.
    let shape = solver.new_constraint_tag();
    for i in 0..n {
        let turned = solver.new_literal();
        for (across, along, case) in [(width[i], length[i], !turned), (length[i], width[i], turned)] {
            // right - left == across
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![right[i].scaled(1), left[i].scaled(-1)],
                    across,
                    shape,
                ))
                .implied_by(case);
            // top - bottom == along
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![top[i].scaled(1), bottom[i].scaled(-1)],
                    along,
                    shape,
                ))
                .implied_by(case);
        }
    }

    // No two containers overlap, and they keep the separation required between
    // their classes: x is at least `sep` left of y, or right of y, or below y,
    // or above y. Each of the four ways has a literal, which at least one of
    // them has to make true.
    let apart = solver.new_constraint_tag();
    let one_way = solver.new_constraint_tag();
    for x in 0..n {
        for y in (x + 1)..n {
            let sep = separation[(classes[x] - 1) as usize][(classes[y] - 1) as usize];
            let ways: Vec<Lit> = (0..4).map(|_| solver.new_literal()).collect();
            // right[x] + sep <= left[y]
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    vec![right[x].scaled(1), left[y].scaled(-1)], -sep, apart))
                .implied_by(ways[0]);
            // left[x] >= right[y] + sep
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    vec![right[y].scaled(1), left[x].scaled(-1)], -sep, apart))
                .implied_by(ways[1]);
            // top[x] + sep <= bottom[y]
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    vec![top[x].scaled(1), bottom[y].scaled(-1)], -sep, apart))
                .implied_by(ways[2]);
            // bottom[x] >= top[y] + sep
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    vec![top[y].scaled(1), bottom[x].scaled(-1)], -sep, apart))
                .implied_by(ways[3]);
            solver
                .add_constraint(pumpkin_solver::clause(ways, one_way))
                .post();
        }
    }

    let mut m = Model::new();
    m.put("left", left);
    m.put("right", right);
    m.put("top", top);
    m.put("bottom", bottom);
    m
}

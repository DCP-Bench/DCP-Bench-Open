// Initials queue: ten people queue for a lecture; each has initials that are an
// alphabetical pair of distinct letters from A..E, no two share initials, and no
// one shares a letter with the person in front. BE is first, CD second and BD
// last. Find the queue (letters as 0..4 for A..E).
//
// The instance has no fields: the queue length, the five letters and the three
// known places are the puzzle's own constants, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 10;
    let letters = 5;
    let (b, c, d, e) = (1, 2, 3, 4);
    let queue: Vec<Vec<Var>> = (0..n)
        .map(|_| (0..2).map(|_| solver.new_bounded_integer(0, letters - 1)).collect())
        .collect();

    // Each person's initials are two distinct letters in alphabetical order.
    let ordered = solver.new_constraint_tag();
    for p in &queue {
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(vec![p[0].scaled(1), p[1].scaled(-1)], -1, ordered))
            .post();
    }

    // No two people have the same initials: the pair, coded as
    // letters * first + second, differs between any two people.
    let distinct = solver.new_constraint_tag();
    let codes: Vec<Var> = queue
        .iter()
        .map(|p| {
            let code = solver.new_bounded_integer(0, letters * letters - 1);
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![p[0].scaled(letters), p[1].scaled(1), code.scaled(-1)],
                    0,
                    distinct,
                ))
                .post();
            code
        })
        .collect();
    solver.add_constraint(pumpkin_solver::all_different(codes, distinct)).post();

    // No one shares a letter with the person in front.
    let neighbours = solver.new_constraint_tag();
    for i in 0..n - 1 {
        for &u in &queue[i] {
            for &v in &queue[i + 1] {
                solver
                    .add_constraint(pumpkin_solver::not_equals(vec![u.scaled(1), v.scaled(-1)], 0, neighbours))
                    .post();
            }
        }
    }

    // BE is at the front, CD right behind, and BD at the end.
    let known = solver.new_constraint_tag();
    for (place, first, second) in [(0, b, e), (1, c, d), (n - 1, b, d)] {
        solver.add_constraint(pumpkin_solver::equals(vec![queue[place][0]], first, known)).post();
        solver.add_constraint(pumpkin_solver::equals(vec![queue[place][1]], second, known)).post();
    }

    let mut m = Model::new();
    m.put("queue", queue);
    m
}

// Golomb ruler: place `size` marks at integer positions, the first at 0 and the
// rest in strictly increasing order, so that all differences between pairs of
// marks are distinct; minimise the position of the last mark (the ruler length).
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let size = inst.size("size"); // number of marks
    let top = (size * size) as i32; // largest position a mark may take, as in the reference

    // marks[i] is the position of mark i. The first mark is at 0 (stated as its
    // domain being just 0); later marks may sit anywhere up to `top`.
    let marks: Vec<Var> = (0..size)
        .map(|i| solver.new_bounded_integer(0, if i == 0 { 0 } else { top }))
        .collect();

    // The marks are strictly increasing: marks[i] < marks[i + 1].
    let increasing = solver.new_constraint_tag();
    for i in 0..size.saturating_sub(1) {
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![marks[i].scaled(1), marks[i + 1].scaled(-1)],
                -1,
                increasing,
            ))
            .post();
    }

    // diffs holds marks[j] - marks[i] for every pair i < j. The marks between i
    // and j give j - i distinct positive gaps, so the difference is at least
    // 1 + 2 + ... + (j - i); that lower bound is implied by the problem and only
    // shrinks the domains.
    let define_diff = solver.new_constraint_tag();
    let mut diffs: Vec<Var> = Vec::new();
    for i in 0..size {
        for j in (i + 1)..size {
            let gaps = (j - i) as i32;
            let d = solver.new_bounded_integer(gaps * (gaps + 1) / 2, top);
            solver
                .add_constraint(pumpkin_solver::equals(
                    vec![marks[j].scaled(1), marks[i].scaled(-1), d.scaled(-1)],
                    0,
                    define_diff,
                ))
                .post();
            diffs.push(d);
        }
    }

    // The Golomb condition: all the pairwise differences are distinct.
    let golomb = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::all_different(diffs, golomb))
        .post();

    // The ruler length is the position of the last mark, which is minimised.
    let length = marks[size - 1];

    let mut m = Model::new();
    m.put("marks", marks);
    m.put("length", length);
    m.minimise(length);
    m
}

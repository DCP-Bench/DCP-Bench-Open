// Five floors: Baker, Cooper, Fletcher, Miller and Smith live on different floors
// 1..5 of an apartment house; find each one's floor from the clues.
//
// The instance has no fields: the five floors and the clues are the puzzle's own
// data, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let floor = |solver: &mut Solver| solver.new_bounded_integer(1, 5);
    let (b, c, f, m, s) = (floor(solver), floor(solver), floor(solver), floor(solver), floor(solver));

    let clues = solver.new_constraint_tag();
    // Baker does not live on the fifth floor.
    solver.add_constraint(pumpkin_solver::not_equals(vec![b], 5, clues)).post();
    // Cooper does not live on the first floor.
    solver.add_constraint(pumpkin_solver::not_equals(vec![c], 1, clues)).post();
    // Fletcher lives on neither the fifth nor the first floor.
    solver.add_constraint(pumpkin_solver::not_equals(vec![f], 5, clues)).post();
    solver.add_constraint(pumpkin_solver::not_equals(vec![f], 1, clues)).post();
    // Miller lives on a higher floor than Cooper: C - M <= -1.
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(vec![c.scaled(1), m.scaled(-1)], -1, clues))
        .post();
    // Smith is not on a floor adjacent to Fletcher's, and Fletcher not on one
    // adjacent to Cooper's: their difference is neither 1 nor -1.
    for (p, q) in [(s, f), (f, c)] {
        for gap in [1, -1] {
            solver
                .add_constraint(pumpkin_solver::not_equals(vec![p.scaled(1), q.scaled(-1)], gap, clues))
                .post();
        }
    }
    // They all live on different floors.
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::all_different(vec![b, c, f, m, s], tag)).post();

    let mut out = Model::new();
    out.put("B", b);
    out.put("C", c);
    out.put("F", f);
    out.put("M", m);
    out.put("S", s);
    out
}

// The Pythagorean triplet whose three numbers add up to 1000.
// The target is the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let x: Vec<Var> = (0..3).map(|_| solver.new_bounded_integer(1, 500)).collect();
    let (a, b, c_side) = (x[0], x[1], x[2]);
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(x.clone(), 1000, tag)).post();

    // a*a + b*b == c*c, each square introduced by a multiplication
    let mut squares: Vec<Var> = Vec::new();
    for side in [a, b, c_side] {
        let square = solver.new_bounded_integer(1, 500 * 500);
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::times(
                side.scaled(1), side.scaled(1), square.scaled(1), tag))
            .post();
        squares.push(square);
    }
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![squares[0].scaled(1), squares[1].scaled(1), squares[2].scaled(-1)],
            0,
            tag,
        ))
        .post();

    let mut m = Model::new();
    m.put("a", a);
    m.put("b", b);
    m.put("c", c_side);
    m
}

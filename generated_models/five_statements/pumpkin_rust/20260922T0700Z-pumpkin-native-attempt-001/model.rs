// Five statements, each claiming how many of the five are false.
// The statements are the puzzle, so the instance carries no fields.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 5;
    let statements: Vec<Lit> = (0..n).map(|_| solver.new_literal()).collect();

    // Statement i says "exactly i+1 of us are false". With n statements, that is
    // n - true == i + 1, so it holds exactly when the number of true ones is
    // n - i - 1. Each statement is therefore reified against that count.
    let counted: Vec<Term> = statements.iter().map(|l| l.get_integer_variable()).collect();
    for i in 0..n {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(
                counted.clone(), (n - i - 1) as i32, tag))
            .reify(statements[i]);
    }

    let mut m = Model::new();
    m.put("statements", statements);
    m
}

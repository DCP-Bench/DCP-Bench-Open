// Four numbers: given up to four numbers between 1 and 10, find three numbers
// between 1 and 10 such that each given number is the sum of some subset of the
// three.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let numbers = inst.ints("numbers"); // the numbers to be produced
    let m = numbers.len();
    let n = 3; // the number of numbers to find (fixed by the problem statement)

    // x[j] is the j-th number to find, between 1 and 10.
    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(1, 10)).collect();
    // uses[i][j] is true when x[j] is part of the sum that makes numbers[i].
    let uses: Vec<Vec<Lit>> = (0..m)
        .map(|_| (0..n).map(|_| solver.new_literal()).collect())
        .collect();

    // contribution[i][j] is x[j] when uses[i][j] holds and 0 otherwise, i.e.
    // uses[i][j] * x[j]: a Boolean times an integer, written with one
    // half-reified equality for each value of the Boolean.
    let taken = solver.new_constraint_tag();
    let skipped = solver.new_constraint_tag();
    let contribution: Vec<Vec<Var>> = (0..m)
        .map(|i| {
            (0..n)
                .map(|j| {
                    let c = solver.new_bounded_integer(0, 10);
                    solver
                        .add_constraint(pumpkin_solver::equals(
                            vec![c.scaled(1), x[j].scaled(-1)], 0, taken))
                        .implied_by(uses[i][j]);
                    solver
                        .add_constraint(pumpkin_solver::equals(vec![c.scaled(1)], 0, skipped))
                        .implied_by(!uses[i][j]);
                    c
                })
                .collect()
        })
        .collect();

    // Each given number is the sum of the numbers it uses.
    let sums = solver.new_constraint_tag();
    for i in 0..m {
        let terms: Vec<Term> = contribution[i].iter().map(|c| c.scaled(1)).collect();
        solver
            .add_constraint(pumpkin_solver::equals(terms, numbers[i], sums))
            .post();
    }

    let mut model = Model::new();
    model.put("x", x);
    model
}

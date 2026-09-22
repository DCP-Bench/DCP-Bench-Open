// Fill the unknown digits of an ISBN-13 so the check digit is right.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let given = inst.ints("isbn_init");
    let n = given.len();

    let isbn: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, 9)).collect();
    for i in 0..n {
        // -1 marks a digit that is not known.
        if given[i] != -1 {
            let tag = solver.new_constraint_tag();
            solver
                .add_constraint(pumpkin_solver::equals(vec![isbn[i].scaled(1)], given[i], tag))
                .post();
        }
    }
    // Every ISBN-13 starts 978 or 979.
    for (position, digit) in [(0usize, 9), (1, 7)] {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(vec![isbn[position].scaled(1)], digit, tag))
            .post();
    }
    let mut third: Vec<Lit> = Vec::new();
    for digit in [8, 9] {
        let flag = solver.new_literal();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(vec![isbn[2].scaled(1)], digit, tag))
            .reify(flag);
        third.push(flag);
    }
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::clause(third, tag)).post();

    // Weights alternate 1, 3 over the first twelve digits.
    let ceiling: i32 = (0..n - 1).map(|i| if i % 2 == 0 { 9 } else { 27 }).sum();
    let weighted_sum = solver.new_bounded_integer(0, ceiling);
    let mut body: Vec<Term> = (0..n - 1)
        .map(|i| isbn[i].scaled(if i % 2 == 0 { 1 } else { 3 }))
        .collect();
    body.push(weighted_sum.scaled(-1));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(body, 0, tag)).post();

    // check == (10 - weighted_sum % 10) % 10, which is exactly
    // (check + weighted_sum) % 10 == 0. Pumpkin has no modulo, so the remainder
    // is introduced explicitly.
    let quotient = solver.new_bounded_integer(0, ceiling / 10);
    let remainder = solver.new_bounded_integer(0, 9);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![weighted_sum.scaled(1), quotient.scaled(-10), remainder.scaled(-1)],
            0,
            tag,
        ))
        .post();
    let combined = solver.new_bounded_integer(0, 18);
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![isbn[n - 1].scaled(1), remainder.scaled(1), combined.scaled(-1)],
            0,
            tag,
        ))
        .post();
    let mut closes: Vec<Lit> = Vec::new();
    for value in [0, 10] {
        let flag = solver.new_literal();
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::equals(vec![combined.scaled(1)], value, tag))
            .reify(flag);
        closes.push(flag);
    }
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::clause(closes, tag)).post();

    let mut m = Model::new();
    m.put("isbn", isbn);
    m
}

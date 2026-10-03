// Even Fibonacci numbers (Project Euler 2): the sum of the even-valued terms of
// the Fibonacci sequence that do not exceed four million.
//
// The instance has no fields: the 35 terms, the limit of four million and the
// bounds 10^7 on a term and 10^8 on the sum are the reference's own constants,
// mirrored here.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 35;
    let limit = 4_000_000;
    let f: Vec<Var> = (0..=n).map(|_| solver.new_bounded_integer(0, 10_000_000)).collect();

    // The sequence starts 0, 1, 1.
    let start = solver.new_constraint_tag();
    for (i, value) in [(0, 0), (1, 1), (2, 1)] {
        solver.add_constraint(pumpkin_solver::equals(vec![f[i]], value, start)).post();
    }

    // Each term is the sum of the previous two.
    let recurrence = solver.new_constraint_tag();
    for i in 3..=n {
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![f[i].scaled(1), f[i - 1].scaled(-1), f[i - 2].scaled(-1)],
                0,
                recurrence,
            ))
            .post();
    }

    // counted[i]: term i is even and below four million. Evenness is written as
    // f[i] == 2 * half + rest with rest in {0, 1}, since Pumpkin has no modulo.
    let selection = solver.new_constraint_tag();
    let mut picked: Vec<Var> = Vec::new();
    for i in 1..=n {
        let half = solver.new_bounded_integer(0, 5_000_000);
        let rest = solver.new_bounded_integer(0, 1);
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![f[i].scaled(1), half.scaled(-2), rest.scaled(-1)],
                0,
                selection,
            ))
            .post();
        let even = solver.new_literal();
        solver.add_constraint(pumpkin_solver::equals(vec![rest], 0, selection)).reify(even);
        let small = solver.new_literal();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(vec![f[i]], limit - 1, selection))
            .reify(small);
        let counted = solver.new_literal();
        solver.add_constraint(pumpkin_solver::clause(vec![!counted, even], selection)).post();
        solver.add_constraint(pumpkin_solver::clause(vec![!counted, small], selection)).post();
        solver.add_constraint(pumpkin_solver::clause(vec![!even, !small, counted], selection)).post();

        // The term's contribution to the sum: f[i] when counted, 0 otherwise.
        let part = solver.new_bounded_integer(0, 10_000_000);
        solver
            .add_constraint(pumpkin_solver::equals(vec![part.scaled(1), f[i].scaled(-1)], 0, selection))
            .implied_by(counted);
        solver.add_constraint(pumpkin_solver::equals(vec![part], 0, selection)).implied_by(!counted);
        picked.push(part);
    }

    // res is the sum of the counted terms.
    let res = solver.new_bounded_integer(0, 100_000_000);
    let mut terms: Vec<Term> = picked.iter().map(|&p| p.scaled(1)).collect();
    terms.push(res.scaled(-1));
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::equals(terms, 0, tag)).post();

    let mut m = Model::new();
    m.put("res", res);
    m
}

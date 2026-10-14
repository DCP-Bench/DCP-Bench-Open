// Low autocorrelation: choose a sequence of n values, each -1 or +1, that
// minimises the sum over shifts k = 1..n-1 of the squared periodic
// autocorrelation C_k = sum_i S_i * S_((i+k) mod n).
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n"); // length of the sequence
    let n_i32 = n as i32;

    // is_plus[i] is true when S_i = +1 and false when S_i = -1. The search is
    // done on these Booleans: the product S_i * S_j is then +1 exactly when the
    // two Booleans agree, which is cheap to state with clauses.
    let is_plus: Vec<Lit> = (0..n).map(|_| solver.new_literal()).collect();

    // sequence[i] is S_i, which is -1 or +1 and never 0 (the reference excludes
    // 0 from the range -1..1). S_i = 2 * is_plus[i] - 1.
    let sequence: Vec<Var> = (0..n).map(|_| solver.new_sparse_integer(vec![-1, 1])).collect();
    let sign = solver.new_constraint_tag();
    for i in 0..n {
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![sequence[i].scaled(1), is_plus[i].get_integer_variable().scaled(-2)],
                -1,
                sign,
            ))
            .post();
    }

    // differ[i][j] (i < j) is true exactly when S_i and S_j have opposite signs,
    // i.e. their product is -1. Stated as the four clauses of an exclusive or.
    let xor_clauses = solver.new_constraint_tag();
    let mut differ: Vec<Vec<Option<Lit>>> = vec![vec![None; n]; n];
    for i in 0..n {
        for j in (i + 1)..n {
            let d = solver.new_literal();
            let (a, b) = (is_plus[i], is_plus[j]);
            for clause in [vec![!d, a, b], vec![!d, !a, !b], vec![d, !a, b], vec![d, a, !b]] {
                solver
                    .add_constraint(pumpkin_solver::clause(clause, xor_clauses))
                    .post();
            }
            differ[i][j] = Some(d);
        }
    }

    // autocorrelation[k-1] is C_k, the periodic autocorrelation at shift k. Of
    // the n products S_i * S_((i+k) mod n), each is +1 or -1, so
    // C_k = n - 2 * (number of products equal to -1); it lies in [-n, n].
    // Each square is C_k * C_k, and the energy is the sum of the squares.
    let shift_tag = solver.new_constraint_tag();
    let square_tag = solver.new_constraint_tag();
    let mut squares: Vec<Var> = Vec::new();
    for k in 1..n {
        let c = solver.new_bounded_integer(-n_i32, n_i32);
        let mut terms: Vec<Term> = vec![c.scaled(1)];
        for i in 0..n {
            let j = (i + k) % n;
            let (lo, hi) = if i < j { (i, j) } else { (j, i) };
            let d = differ[lo][hi].expect("pair literal exists");
            terms.push(d.get_integer_variable().scaled(2));
        }
        solver
            .add_constraint(pumpkin_solver::equals(terms, n_i32, shift_tag))
            .post();
        let square = solver.new_bounded_integer(0, n_i32 * n_i32);
        solver
            .add_constraint(pumpkin_solver::times(c, c, square, square_tag))
            .post();
        squares.push(square);
    }

    // energy = sum of the squared autocorrelations, to be minimised. Its upper
    // bound is n - 1 shifts, each at most n squared.
    let energy = solver.new_bounded_integer(0, (n_i32 - 1).max(0) * n_i32 * n_i32);
    let mut terms: Vec<Term> = squares.iter().map(|s| s.scaled(1)).collect();
    terms.push(energy.scaled(-1));
    let total = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, total))
        .post();

    let mut m = Model::new();
    m.put("sequence", sequence);
    m.minimise(energy);
    m
}

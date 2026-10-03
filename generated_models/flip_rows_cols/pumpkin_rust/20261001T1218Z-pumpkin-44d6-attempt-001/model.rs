// Flip rows and columns: given a matrix of numbers, choose a sign (+1 or -1) for
// every row and every column, flipping the sign of the entries in it, so that
// every row sum and every column sum is zero or positive and the total of all
// entries is as small as possible.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let input_matrix = inst.matrix("input_matrix");
    let rows = input_matrix.len();
    let cols = input_matrix[0].len();

    // The signs are -1 or +1, never 0. The search is done on Booleans:
    // plus_row[i] / plus_col[j] is true when that row / column keeps its sign
    // (+1); the sign variables are 2 * flag - 1.
    let plus_row: Vec<Lit> = (0..rows).map(|_| solver.new_literal()).collect();
    let plus_col: Vec<Lit> = (0..cols).map(|_| solver.new_literal()).collect();
    let row_signs: Vec<Var> = (0..rows).map(|_| solver.new_sparse_integer(vec![-1, 1])).collect();
    let col_signs: Vec<Var> = (0..cols).map(|_| solver.new_sparse_integer(vec![-1, 1])).collect();
    let sign = solver.new_constraint_tag();
    for i in 0..rows {
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![row_signs[i].scaled(1), plus_row[i].get_integer_variable().scaled(-2)], -1, sign))
            .post();
    }
    for j in 0..cols {
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![col_signs[j].scaled(1), plus_col[j].get_integer_variable().scaled(-2)], -1, sign))
            .post();
    }

    // keeps[i][j] is true when the entry (i, j) keeps its sign: its row sign and
    // its column sign are equal, so their product is +1. The new entry is then
    // input_matrix[i][j], otherwise -input_matrix[i][j]. keeps is an
    // "equivalence" of two Booleans, stated as four clauses.
    let equivalence = solver.new_constraint_tag();
    let mut keeps: Vec<Vec<Lit>> = Vec::new();
    for i in 0..rows {
        let mut row: Vec<Lit> = Vec::new();
        for j in 0..cols {
            let k = solver.new_literal();
            let (r, c) = (plus_row[i], plus_col[j]);
            for clause in [vec![!k, !r, c], vec![!k, r, !c], vec![k, r, c], vec![k, !r, !c]] {
                solver
                    .add_constraint(pumpkin_solver::clause(clause, equivalence))
                    .post();
            }
            row.push(k);
        }
        keeps.push(row);
    }

    // The entry after flipping is x[i][j] = M[i][j] * row_sign * col_sign
    // = M[i][j] * (2 * keeps[i][j] - 1). A sum of entries over some cells is
    // therefore the sum of 2 * M[i][j] * keeps[i][j] minus the sum of M[i][j].
    // Entries equal to 0 are left out of these sums (Pumpkin cannot take a zero
    // coefficient); they contribute nothing either way.

    // Each row sum is at least 0; the reference bounds it by 300.
    let row_sum_tag = solver.new_constraint_tag();
    for i in 0..rows {
        let row_sum = solver.new_bounded_integer(0, 300);
        let mut terms: Vec<Term> = vec![row_sum.scaled(1)];
        let mut base = 0;
        for j in 0..cols {
            let m = input_matrix[i][j];
            if m != 0 {
                terms.push(keeps[i][j].get_integer_variable().scaled(-2 * m));
                base -= m;
            }
        }
        // row_sum - sum(2 M keeps) = -sum(M)
        solver
            .add_constraint(pumpkin_solver::equals(terms, base, row_sum_tag))
            .post();
    }

    // Each column sum is at least 0; the reference bounds it by 300.
    let col_sum_tag = solver.new_constraint_tag();
    for j in 0..cols {
        let col_sum = solver.new_bounded_integer(0, 300);
        let mut terms: Vec<Term> = vec![col_sum.scaled(1)];
        let mut base = 0;
        for i in 0..rows {
            let m = input_matrix[i][j];
            if m != 0 {
                terms.push(keeps[i][j].get_integer_variable().scaled(-2 * m));
                base -= m;
            }
        }
        solver
            .add_constraint(pumpkin_solver::equals(terms, base, col_sum_tag))
            .post();
    }

    // total_sum is the sum of all entries after flipping, to be minimised. Its
    // bounds are 0 and 1000, as in the reference.
    let total_sum = solver.new_bounded_integer(0, 1000);
    let mut terms: Vec<Term> = vec![total_sum.scaled(1)];
    let mut base = 0;
    for i in 0..rows {
        for j in 0..cols {
            let m = input_matrix[i][j];
            if m != 0 {
                terms.push(keeps[i][j].get_integer_variable().scaled(-2 * m));
                base -= m;
            }
        }
    }
    let total_tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, base, total_tag))
        .post();

    let mut m = Model::new();
    m.put("row_signs", row_signs);
    m.put("col_signs", col_signs);
    m.minimise(total_sum);
    m
}

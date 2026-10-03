// Hadamard matrix (Legendre pairs): find two sequences a and b of length l,
// every entry -1 or +1, each adding up to 1, whose periodic autocorrelations
// satisfy PAF(a, s) + PAF(b, s) = -2 for every shift s = 1 .. (l - 1) / 2.
// PAF(a, s) = sum_i a_i * a_((i+s) mod l).

type Tag = pumpkin_solver::core::proof::ConstraintTag;

// The sequence `values` of -1/+1 entries, built from the Booleans `is_plus`
// (is_plus[i] true means entry i is +1). Returns the entries as variables and,
// for each shift s = 1 .. m, the Booleans that say which of the l products
// a_i * a_((i+s) mod l) are -1 (the two entries differ).
fn sequence(solver: &mut Solver, l: usize, m: usize, tag: Tag) -> (Vec<Var>, Vec<Lit>, Vec<Vec<Lit>>) {
    let is_plus: Vec<Lit> = (0..l).map(|_| solver.new_literal()).collect();
    // Entry i is -1 or +1, never 0; entry = 2 * is_plus - 1.
    let entries: Vec<Var> = (0..l).map(|_| solver.new_sparse_integer(vec![-1, 1])).collect();
    for i in 0..l {
        solver
            .add_constraint(pumpkin_solver::equals(
                vec![entries[i].scaled(1), is_plus[i].get_integer_variable().scaled(-2)],
                -1,
                tag,
            ))
            .post();
    }
    // differ[s-1][i] is true exactly when entries i and (i+s) mod l have opposite
    // signs (their product is -1), stated as the four clauses of an exclusive or.
    let mut differ: Vec<Vec<Lit>> = Vec::new();
    for s in 1..=m {
        let mut row: Vec<Lit> = Vec::new();
        for i in 0..l {
            let (x, y) = (is_plus[i], is_plus[(i + s) % l]);
            let d = solver.new_literal();
            for clause in [vec![!d, x, y], vec![!d, !x, !y], vec![d, !x, y], vec![d, x, !y]] {
                solver
                    .add_constraint(pumpkin_solver::clause(clause, tag))
                    .post();
            }
            row.push(d);
        }
        differ.push(row);
    }
    (entries, is_plus, differ)
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let l = inst.size("l"); // length of each sequence, an odd number
    let m = (l - 1) / 2; // number of shifts that are constrained

    let sign_a = solver.new_constraint_tag();
    let sign_b = solver.new_constraint_tag();
    let (a, a_plus, a_differ) = sequence(solver, l, m, sign_a);
    let (b, b_plus, b_differ) = sequence(solver, l, m, sign_b);

    // Each sequence adds up to 1: sum(entries) = 2 * (number of +1 entries) - l = 1.
    let sums = solver.new_constraint_tag();
    for plus in [&a_plus, &b_plus] {
        let terms: Vec<Term> = plus.iter().map(|p| p.get_integer_variable().scaled(2)).collect();
        solver
            .add_constraint(pumpkin_solver::equals(terms, l as i32 + 1, sums))
            .post();
    }

    // For every shift s: PAF(a, s) + PAF(b, s) = -2. A sequence has l products
    // a_i * a_(i+s), each +1 or -1, so PAF = l - 2 * (number of -1 products), and
    // the requirement becomes: the numbers of -1 products in a and in b add up to l + 1.
    let autocorrelation = solver.new_constraint_tag();
    for s in 0..m {
        let mut both: Vec<Lit> = a_differ[s].clone();
        both.extend(b_differ[s].iter());
        let target = solver.new_bounded_integer(l as i32 + 1, l as i32 + 1);
        solver
            .add_constraint(pumpkin_solver::boolean_equals(vec![1; 2 * l], both, target, autocorrelation))
            .post();
    }

    let mut model = Model::new();
    model.put("a", a);
    model.put("b", b);
    model
}

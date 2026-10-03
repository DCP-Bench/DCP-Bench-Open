// Handshaking: Hilary and Jocelyn are a couple who invite num_couples other couples.
// Everyone shakes hands with some of the others, never with themselves or their own
// spouse, and everyone except Hilary has shaken a different number of hands.
// Find how many hands Hilary has shaken.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let num_couples = inst.size("num_couples");
    // The people are numbered so that persons 2k and 2k+1 are a couple; Hilary is
    // person 0 and Jocelyn is person 1.
    let n = 2 + 2 * num_couples;
    let most = n as i32 - 2; // nobody shakes hands with themselves or their spouse

    // shake[i][j] is true when persons i and j shake hands. There is no literal
    // for a person with themselves or with their spouse (they never shake hands).
    // Handshaking is symmetric (a shakes b exactly when b shakes a), so the two
    // orders of a pair share one literal instead of two linked by an equality.
    let mut shake: Vec<Vec<Option<Lit>>> = vec![vec![None; n]; n];
    for i in 0..n {
        for j in (i + 1)..n {
            if i / 2 != j / 2 {
                let lit = solver.new_literal();
                shake[i][j] = Some(lit);
                shake[j][i] = Some(lit);
            }
        }
    }

    // x[i] is the number of hands person i has shaken: the number of true
    // literals in row i. It is between 0 and n - 2.
    let counted = solver.new_constraint_tag();
    let x: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, most)).collect();
    for i in 0..n {
        let lits: Vec<Lit> = (0..n).filter_map(|j| shake[i][j]).collect();
        if lits.is_empty() {
            solver
                .add_constraint(pumpkin_solver::equals(vec![x[i].scaled(1)], 0, counted))
                .post();
        } else {
            solver
                .add_constraint(pumpkin_solver::boolean_equals(
                    vec![1; lits.len()], lits, x[i], counted))
                .post();
        }
    }

    // Everyone except Hilary has shaken a different number of hands.
    let differ = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::all_different(x[1..].to_vec(), differ))
        .post();

    // Implied constraint, added to help the solver: the n - 1 different counts of
    // everyone except Hilary all lie in 0..n-2, which holds n - 1 values, so they
    // are exactly 0, 1, ..., n-2 in some order and their sum is fixed.
    let total = (n as i32 - 1) * (n as i32 - 2) / 2;
    let permutation = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            x[1..].iter().map(|v| v.scaled(1)).collect::<Vec<Term>>(), total, permutation))
        .post();

    // Symmetry breaking derived here (the reference has none): the invited couples
    // are interchangeable, and so are the two spouses within an invited couple.
    // Renumbering couples, or swapping two spouses, maps a valid handshake pattern
    // to another valid one with the same count for Hilary, so the declared output
    // keeps every value it can take. Within each invited couple the first spouse
    // has shaken more hands than the second (the counts differ, as all counts
    // except Hilary's do), and the first spouses' counts increase from couple to
    // couple. Without this, ruling out a second answer for six or more couples
    // timed out.
    let spouses = solver.new_constraint_tag();
    let couples = solver.new_constraint_tag();
    for k in 1..=num_couples {
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![x[2 * k + 1].scaled(1), x[2 * k].scaled(-1)], -1, spouses))
            .post();
        if k < num_couples {
            solver
                .add_constraint(pumpkin_solver::less_than_or_equals(
                    vec![x[2 * k].scaled(1), x[2 * k + 2].scaled(-1)], -1, couples))
                .post();
        }
    }

    // The answer: the number of hands Hilary has shaken.
    let mut m = Model::new();
    m.put("hil", x[0]);
    m
}

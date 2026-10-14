// Word design: find a set of DNA words of equal length such that every word has
// four letters from {C,G}, any two different words differ in at least four
// positions, and the reverse of any word (itself included) differs in at least
// four positions from the Watson-Crick complement of any word.

// Require that at least `needed` of the position literals in `differ` hold.
// Pumpkin has no cardinality constraint, so this is "at most len - needed of
// them are false", written with boolean_less_than_or_equals over the negations.
fn at_least_differ(
    solver: &mut Solver,
    differ: &[Lit],
    needed: usize,
    tag: pumpkin_solver::core::proof::ConstraintTag,
) {
    let negated: Vec<Lit> = differ.iter().map(|&d| !d).collect();
    solver
        .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
            vec![1; negated.len()], negated, (differ.len() - needed) as i32, tag))
        .post();
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.size("n"); // length of each word
    let num_words = inst.size("num_words"); // number of words to find

    // The problem statement fixes these, they are not instance fields: letters are
    // 1 = A, 2 = C, 3 = G, 4 = T; every word has 4 letters from {C,G}; and the
    // required Hamming distances are 4.
    let cg_letters = 4;
    let min_distance = 4;

    // words[i][j] is the j-th letter of word i.
    let words: Vec<Vec<Var>> = (0..num_words)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(1, 4)).collect())
        .collect();

    // letter_is[i][j][v] is true exactly when words[i][j] == v + 1. Pumpkin has no
    // count constraint, so the counting and comparison below go through these literals.
    let channel = solver.new_constraint_tag();
    let mut letter_is: Vec<Vec<Vec<Lit>>> = Vec::new();
    for i in 0..num_words {
        let mut per_word: Vec<Vec<Lit>> = Vec::new();
        for j in 0..n {
            let mut per_letter: Vec<Lit> = Vec::new();
            for v in 0..4 {
                let flag = solver.new_literal();
                solver
                    .add_constraint(pumpkin_solver::equals(
                        vec![words[i][j].scaled(1)], v + 1, channel))
                    .reify(flag);
                per_letter.push(flag);
            }
            per_word.push(per_letter);
        }
        letter_is.push(per_word);
    }

    // Each word has exactly cg_letters letters that are C or G.
    let cg_count = solver.new_bounded_integer(cg_letters, cg_letters);
    let cg_tag = solver.new_constraint_tag();
    for i in 0..num_words {
        let mut cg: Vec<Lit> = Vec::new();
        for j in 0..n {
            cg.push(letter_is[i][j][1]); // C
            cg.push(letter_is[i][j][2]); // G
        }
        solver
            .add_constraint(pumpkin_solver::boolean_equals(vec![1; cg.len()], cg, cg_count, cg_tag))
            .post();
    }

    // Each pair of different words differs in at least min_distance positions.
    // differ[j] is made to imply that position j really differs (the two words
    // have no letter in common there); it may be false when they do differ, which
    // only makes the requirement harder to meet, never easier.
    let same_letter = solver.new_constraint_tag();
    let distinct = solver.new_constraint_tag();
    for x in 0..num_words {
        for y in (x + 1)..num_words {
            let mut differ: Vec<Lit> = Vec::new();
            for j in 0..n {
                let flag = solver.new_literal();
                for v in 0..4 {
                    solver
                        .add_constraint(pumpkin_solver::clause(
                            vec![!flag, !letter_is[x][j][v], !letter_is[y][j][v]], same_letter))
                        .post();
                }
                differ.push(flag);
            }
            at_least_differ(solver, &differ, min_distance, distinct);
        }
    }

    // For every pair of words x and y, identical or not, the reverse of x and the
    // Watson-Crick complement of y (A<->T, C<->G, i.e. letter l becomes 5 - l)
    // differ in at least min_distance positions. Position j compares the letter
    // x[n-1-j] with the complement of y[j]; they are equal when x[n-1-j] = v + 1
    // and y[j] = 4 - v, i.e. letter index v for x and 3 - v for y.
    let complement = solver.new_constraint_tag();
    let reverse_complement = solver.new_constraint_tag();
    for x in 0..num_words {
        for y in 0..num_words {
            let mut differ: Vec<Lit> = Vec::new();
            for j in 0..n {
                let flag = solver.new_literal();
                for v in 0..4 {
                    solver
                        .add_constraint(pumpkin_solver::clause(
                            vec![!flag, !letter_is[x][n - 1 - j][v], !letter_is[y][j][3 - v]],
                            complement))
                        .post();
                }
                differ.push(flag);
            }
            at_least_differ(solver, &differ, min_distance, reverse_complement);
        }
    }

    let mut m = Model::new();
    m.put("words", words);
    m
}

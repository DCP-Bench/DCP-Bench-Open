// Archery puzzle: choose how many arrows hit each target so that the total score
// comes as close as possible to the target score.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let targets = inst.ints("targets"); // points scored by one arrow on each target
    let target_score = inst.int("target_score"); // the total the archer is aiming for
    let n = targets.len();

    // hits[i] is the number of arrows on target i, as in the reference from 0 to target_score.
    let hits: Vec<Var> = (0..n).map(|_| solver.new_bounded_integer(0, target_score)).collect();
    // score is the total scored, and gap is the signed distance target_score - score.
    // The bounds 0..2*target_score and -target_score..target_score are the reference's.
    let score = solver.new_bounded_integer(0, target_score * 2);
    let gap = solver.new_bounded_integer(-target_score, target_score);
    // deviation is how far the score is from the target score, the quantity to minimise.
    let deviation = solver.new_bounded_integer(0, target_score * 2);

    // score = sum(hits * targets). A target worth 0 points would give a zero
    // coefficient, which Pumpkin cannot take, so it is left out of the sum.
    let mut terms: Vec<Term> = hits
        .iter()
        .zip(&targets)
        .filter(|(_, &points)| points != 0)
        .map(|(&h, &points)| h.scaled(points))
        .collect();
    terms.push(score.scaled(-1));
    let total = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(terms, 0, total))
        .post();

    // gap = target_score - score, written as gap + score = target_score.
    let distance = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![gap.scaled(1), score.scaled(1)], target_score, distance))
        .post();

    // deviation = |target_score - score|
    let absolute = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::absolute(gap, deviation, absolute))
        .post();

    let mut m = Model::new();
    m.put("hits", hits);
    m.minimise(deviation);
    m
}

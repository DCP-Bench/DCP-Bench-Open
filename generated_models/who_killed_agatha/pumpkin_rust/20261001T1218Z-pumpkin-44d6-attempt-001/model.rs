// Who killed Agatha: Agatha, the butler and Charles live in Dreadsbury Mansion and
// one of them killed Agatha. From who hates whom and who is richer than whom,
// find the killer (0-based index into names).
//
// The number of residents comes from the instance's names; the roles of
// residents 0 (Agatha), 1 (the butler) and 2 (Charles) and the statements are
// the puzzle's own data, mirrored from the reference.
fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n = inst.len("names");
    let (agatha, butler, charles) = (0, 1, 2);
    let victim = agatha;

    let killer = solver.new_bounded_integer(0, n as i32 - 1);
    // hates[i][j]: i hates j. richer[i][j]: i is richer than j.
    let hates: Vec<Vec<Lit>> = (0..n).map(|_| (0..n).map(|_| solver.new_literal()).collect()).collect();
    let richer: Vec<Vec<Lit>> = (0..n).map(|_| (0..n).map(|_| solver.new_literal()).collect()).collect();

    // A killer always hates, and is no richer than, his victim.
    let killer_tag = solver.new_constraint_tag();
    for k in 0..n {
        let is_killer = solver.new_literal();
        solver
            .add_constraint(pumpkin_solver::equals(vec![killer], k as i32, killer_tag))
            .reify(is_killer);
        solver.add_constraint(pumpkin_solver::clause(vec![!is_killer, hates[k][victim]], killer_tag)).post();
        solver.add_constraint(pumpkin_solver::clause(vec![!is_killer, !richer[k][victim]], killer_tag)).post();
    }

    // Nobody is richer than himself, and of two different people exactly one is
    // richer than the other.
    let richness = solver.new_constraint_tag();
    for i in 0..n {
        solver.add_constraint(pumpkin_solver::clause(vec![!richer[i][i]], richness)).post();
        for j in (i + 1)..n {
            solver.add_constraint(pumpkin_solver::clause(vec![richer[i][j], richer[j][i]], richness)).post();
            solver.add_constraint(pumpkin_solver::clause(vec![!richer[i][j], !richer[j][i]], richness)).post();
        }
    }

    // Charles hates no one that Agatha hates.
    let tag = solver.new_constraint_tag();
    for i in 0..n {
        solver.add_constraint(pumpkin_solver::clause(vec![!hates[agatha][i], !hates[charles][i]], tag)).post();
    }

    // Agatha hates everybody except the butler.
    let tag = solver.new_constraint_tag();
    for (person, hated) in [(agatha, true), (charles, true), (butler, false)] {
        let l = if hated { hates[agatha][person] } else { !hates[agatha][person] };
        solver.add_constraint(pumpkin_solver::clause(vec![l], tag)).post();
    }

    // The butler hates everyone not richer than Aunt Agatha.
    let tag = solver.new_constraint_tag();
    for i in 0..n {
        solver.add_constraint(pumpkin_solver::clause(vec![richer[i][agatha], hates[butler][i]], tag)).post();
    }

    // The butler hates everyone whom Agatha hates.
    let tag = solver.new_constraint_tag();
    for i in 0..n {
        solver.add_constraint(pumpkin_solver::clause(vec![!hates[agatha][i], hates[butler][i]], tag)).post();
    }

    // No one hates everyone: each person hates at most n - 1 people.
    let tag = solver.new_constraint_tag();
    for i in 0..n {
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(vec![1; n], hates[i].clone(), n as i32 - 1, tag))
            .post();
    }

    let mut m = Model::new();
    m.put("killer", killer);
    m
}

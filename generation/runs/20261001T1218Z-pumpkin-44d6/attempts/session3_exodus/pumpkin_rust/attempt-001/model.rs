// Exodus: five children each present a different part of the Exodus story, have
// a different age and come from a different country. Every entity gets a slot
// 1..5; entities sharing a slot belong to the same child. Find the matching.
//
// The instance has no fields: the entities, the ages 3, 5, 7, 8, 10 and the five
// clues are the puzzle's own data, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 5;
    let age_values = [3, 5, 7, 8, 10];
    let group = |solver: &mut Solver| -> Vec<Var> { (0..n).map(|_| solver.new_bounded_integer(1, n)).collect() };
    let ages = group(solver);
    let children = group(solver);
    let countries = group(solver);
    let stories = group(solver);
    let (bernice, _carl, debby, sammy, ted) = (children[0], children[1], children[2], children[3], children[4]);
    let (ethiopia, _kazakhstan, lithuania, morocco, yemen) =
        (countries[0], countries[1], countries[2], countries[3], countries[4]);
    let (_burning_bush, _captivity, moses_youth, passover, _ten_commandments) =
        (stories[0], stories[1], stories[2], stories[3], stories[4]);

    // Within each category every entity has its own slot.
    let tag = solver.new_constraint_tag();
    for g in [&ages, &children, &countries, &stories] {
        solver.add_constraint(pumpkin_solver::all_different(g.clone(), tag)).post();
    }

    // 1. Debby's family is from Lithuania.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(vec![debby.scaled(1), lithuania.scaled(-1)], 0, tag))
        .post();

    // Clues 2-5 compare the ages of two children. As in the reference: for every
    // pair of ages (a1, a2) that violates the relation, the first child cannot
    // have age a1 while the second has age a2, i.e. not (slot of a1 == first and
    // slot of a2 == second).
    let same_slot = |solver: &mut Solver, p: Var, q: Var, tag| -> Lit {
        let l = solver.new_literal();
        solver.add_constraint(pumpkin_solver::equals(vec![p.scaled(1), q.scaled(-1)], 0, tag)).reify(l);
        l
    };
    let compare = |solver: &mut Solver, first: Var, second: Var, holds: &dyn Fn(i32, i32) -> bool| {
        let tag = solver.new_constraint_tag();
        for k1 in 0..ages.len() {
            for k2 in 0..ages.len() {
                if !holds(age_values[k1], age_values[k2]) {
                    let x = same_slot(solver, ages[k1], first, tag);
                    let y = same_slot(solver, ages[k2], second, tag);
                    solver.add_constraint(pumpkin_solver::clause(vec![!x, !y], tag)).post();
                }
            }
        }
    };
    // 2. The Passover child is two years older than Bernice.
    compare(solver, passover, bernice, &|a1, a2| a1 == a2 + 2);
    // 3. The Yemeni child is younger than the Ethiopian child.
    compare(solver, yemen, ethiopia, &|a1, a2| a1 < a2);
    // 4. The Moroccan child is three years older than Ted.
    compare(solver, morocco, ted, &|a1, a2| a1 == a2 + 3);
    // 5. Sammy is three years older than the child who told of Moses's youth.
    compare(solver, sammy, moses_youth, &|a1, a2| a1 == a2 + 3);

    let mut m = Model::new();
    m.put("ages", ages);
    m.put("children", children);
    m.put("countries", countries);
    m.put("stories", stories);
    m
}

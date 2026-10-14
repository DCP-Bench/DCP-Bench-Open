// Zebra puzzle: five houses in a row (0..4, left to right), each with a different
// colour, nationality, pet, drink and job. Each output gives the house of every
// colour, nationality, job, pet and drink.
//
// The instance has no fields: the attributes and the clues are the puzzle's own
// data, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let n = 5;
    let group = |solver: &mut Solver| -> Vec<Var> { (0..n).map(|_| solver.new_bounded_integer(0, n - 1)).collect() };
    let colors = group(solver);
    let nations = group(solver);
    let jobs = group(solver);
    let pets = group(solver);
    let drinks = group(solver);
    let (_yellow, green, red, white, blue) = (colors[0], colors[1], colors[2], colors[3], colors[4]);
    let (italy, spain, japan, england, norway) = (nations[0], nations[1], nations[2], nations[3], nations[4]);
    let (painter, sculptor, diplomat, _pianist, doctor) = (jobs[0], jobs[1], jobs[2], jobs[3], jobs[4]);
    let (_cat, zebra, _bear, snails, horse) = (pets[0], pets[1], pets[2], pets[3], pets[4]);
    let (milk, _water, _tea, coffee, _juice) = (drinks[0], drinks[1], drinks[2], drinks[3], drinks[4]);

    // Each house has a different colour, nationality, job, pet and drink.
    let tag = solver.new_constraint_tag();
    for g in [&colors, &nations, &jobs, &pets, &drinks] {
        solver.add_constraint(pumpkin_solver::all_different(g.clone(), tag)).post();
    }

    // p lives offset houses to the right of q: p - q == offset.
    let clues = solver.new_constraint_tag();
    let same = |solver: &mut Solver, p: Var, q: Var, offset: i32| {
        solver.add_constraint(pumpkin_solver::equals(vec![p.scaled(1), q.scaled(-1)], offset, clues)).post();
    };
    same(solver, painter, horse, 0); // the painter owns the horse
    same(solver, diplomat, coffee, 0); // the diplomat drinks coffee
    same(solver, white, milk, 0); // the milk drinker lives in the white house
    same(solver, spain, painter, 0); // the Spaniard is a painter
    same(solver, england, red, 0); // the Englishman lives in the red house
    same(solver, snails, sculptor, 0); // the sculptor owns the snails
    same(solver, red, green, 1); // the green house is immediately left of the red one
    same(solver, norway, blue, 1); // the Norwegian lives immediately right of the blue house
    same(solver, doctor, milk, 0); // the doctor drinks milk
    same(solver, japan, diplomat, 0); // the diplomat is Japanese
    same(solver, norway, zebra, 0); // the Norwegian owns the zebra

    // Next-door houses, as allowed (p, q) pairs with |p - q| == 1.
    let adjacent: Vec<Vec<i32>> = (0..n)
        .flat_map(|p| (0..n).map(move |q| (p, q)))
        .filter(|&(p, q)| (p - q).abs() == 1)
        .map(|(p, q)| vec![p, q])
        .collect();
    // The green house is next to the white one.
    solver.add_constraint(pumpkin_solver::table(vec![green, white], adjacent.clone(), clues)).post();
    // The horse is owned by the diplomat's neighbour.
    solver.add_constraint(pumpkin_solver::table(vec![horse, diplomat], adjacent, clues)).post();

    // The Italian lives in the red, the white or the green house.
    let in_house: Vec<Lit> = [red, white, green]
        .iter()
        .map(|&h| {
            let l = solver.new_literal();
            solver
                .add_constraint(pumpkin_solver::equals(vec![italy.scaled(1), h.scaled(-1)], 0, clues))
                .reify(l);
            l
        })
        .collect();
    solver.add_constraint(pumpkin_solver::clause(in_house, clues)).post();

    let mut m = Model::new();
    m.put("colors", colors);
    m.put("nations", nations);
    m.put("jobs", jobs);
    m.put("pets", pets);
    m.put("drinks", drinks);
    m
}

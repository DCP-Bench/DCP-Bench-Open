// Nontransitive dice for Rock-Paper-Scissors-Lizard-Spock: five six-faced dice
// with faces 1..12 such that each of the ten "beats" relations of the game holds,
// where die A beats die B when A shows the larger face in more than half of the
// 36 face pairs.
//
// The instance has no fields: the number of dice and faces, the face range and
// the ten relations are the puzzle's own constants, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let (rock, paper, scissors, lizard, spock) = (0, 1, 2, 3, 4);
    let m = 5; // number of dice
    let n = 6; // faces per die
    let f = 12; // largest face value
    let edges: [(usize, usize); 10] = [
        (rock, scissors),     // Rock crushes Scissors
        (rock, lizard),       // Rock crushes Lizard
        (paper, rock),        // Paper covers Rock
        (paper, spock),       // Paper disproves Spock
        (scissors, paper),    // Scissors cuts Paper
        (scissors, lizard),   // Scissors decapitates Lizard
        (lizard, paper),      // Lizard eats Paper
        (lizard, spock),      // Lizard poisons Spock
        (spock, rock),        // Spock vaporizes Rock
        (spock, scissors),    // Spock smashes Scissors
    ];

    // dice[i][j]: the value on face j of die i.
    let dice: Vec<Vec<Var>> = (0..m)
        .map(|_| (0..n).map(|_| solver.new_bounded_integer(1, f)).collect())
        .collect();

    // For each relation, the winner shows the strictly larger face in more than
    // half of the n * n face pairs. wins[x][y] holds exactly when
    // dice[winner][x] > dice[loser][y], i.e. loser - winner <= -1. "More than half"
    // is at least n*n/2 + 1 true literals, posted as at most n*n - (n*n/2 + 1)
    // false ones, since Pumpkin has no lower-bounded cardinality.
    let pairs = (n * n) as i32;
    let needed = pairs / 2 + 1;
    let face_wins = solver.new_constraint_tag();
    let beats = solver.new_constraint_tag();
    for &(winner, loser) in edges.iter() {
        let mut losses: Vec<Lit> = Vec::with_capacity(n * n);
        for x in 0..n {
            for y in 0..n {
                let win = solver.new_literal();
                solver
                    .add_constraint(pumpkin_solver::less_than_or_equals(
                        vec![dice[loser][y].scaled(1), dice[winner][x].scaled(-1)],
                        -1,
                        face_wins,
                    ))
                    .reify(win);
                losses.push(!win);
            }
        }
        solver
            .add_constraint(pumpkin_solver::boolean_less_than_or_equals(
                vec![1; losses.len()],
                losses,
                pairs - needed,
                beats,
            ))
            .post();
    }

    let mut model = Model::new();
    model.put("dice", dice);
    model
}

// Nontransitive dice: five dice (Rock, Paper, Scissors, Lizard, Spock), six faces each,
// face values in 1..=12. The beats relation between two dice A and B holds when A has a
// strictly larger face than B in more than half of the 36 face pairs (at least 19).
// Die indices: 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock.

// Each die has six faces, each face value between 1 and 12 inclusive.
// Face values may repeat, both within a die and across dice.
fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let _ = inst;
    let n_dice = 5usize;
    let n_faces = 6usize;
    let mut dice: Vec<Vec<IntVar>> = Vec::new();
    for _ in 0..n_dice {
        let mut die = Vec::new();
        for _ in 0..n_faces {
            die.push(IntVar::new(1..=12));
        }
        dice.push(die);
    }

    // Each beats relationship between two dice is a count of strictly larger face pairs
    // over all 36 pairs of faces, and must exceed half of them: at least 19 pairs.
    // a_gt_b(a, b) is a literal true exactly when face a is strictly larger than face b.
    let beats: [(usize, usize); 10] = [
        (0, 2), // Rock(1) crushes Scissors(3)
        (0, 3), // Rock(1) crushes Lizard(4)
        (1, 0), // Paper(2) covers Rock(1)
        (1, 4), // Paper(2) disproves Spock(5)
        (2, 1), // Scissors(3) cuts Paper(2)
        (2, 3), // Scissors(3) decapitate Lizard(4)
        (3, 1), // Lizard(4) eats Paper(2)
        (3, 4), // Lizard(4) poisons Spock(5)
        (4, 0), // Spock(5) vaporizes Rock(1)
        (4, 2), // Spock(5) smashes Scissors(3)
    ];

    for &(a, b) in beats.iter() {
        // A has a strictly larger face value than die B in more than half of all possible pairs of faces.
        let mut wins = LinExp::default();
        for k in 0..n_faces {
            for l in 0..n_faces {
                // face a_k > face b_l, that is not (a_k - b_l <= 0)
                let le = reify_le(s, iv(&dice[a][k]) - iv(&dice[b][l]), 0)?;
                wins += LinExp::from(!le);
            }
        }
        post(s, wins, Comparator::GreaterEq, 19)?;
    }

    let mut out = Out::new();
    out.put("dice", &dice);
    Ok(out)
}

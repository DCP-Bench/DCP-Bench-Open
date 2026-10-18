// Nontransitive dice: five dice (Rock, Paper, Scissors, Lizard, Spock), each with
// six faces whose values lie in 1..12 inclusive. Values may repeat within and
// across dice.
// A die A beats die B when A has a strictly larger face than B in more than half
// of the 36 face pairs (more than 18 pairs).
// The ten beats relationships of Rock-Paper-Scissors-Lizard-Spock must hold:
//   Rock crushes Scissors, Rock crushes Lizard, Paper covers Rock,
//   Paper disproves Spock, Scissors cuts Paper, Scissors decapitate Lizard,
//   Lizard eats Paper, Lizard poisons Spock, Spock vaporizes Rock,
//   Spock smashes Scissors.
// Indices are 0-based: Rock 0, Paper 1, Scissors 2, Lizard 3, Spock 4.

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let _ = inst;

    // Six faces per die, values 1..=12.
    let mut dice: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..5 {
        dice.push(m.new_int_decisions(6, 1..=12));
    }

    // Each beats pair (winner, loser) as 0-based die indices.
    let beats: [(usize, usize); 10] = [
        (0, 2), // Rock crushes Scissors
        (0, 3), // Rock crushes Lizard
        (1, 0), // Paper covers Rock
        (1, 4), // Paper disproves Spock
        (2, 1), // Scissors cuts Paper
        (2, 3), // Scissors decapitate Lizard
        (3, 1), // Lizard eats Paper
        (3, 4), // Lizard poisons Spock
        (4, 0), // Spock vaporizes Rock
        (4, 2), // Spock smashes Scissors
    ];

    // The winner has a strictly larger face in at least 19 of the 36 face pairs.
    for (a, b) in beats {
        let mut wins: Vec<View<bool>> = Vec::new();
        for fa in 0..6 {
            for fb in 0..6 {
                let w = m.linear(dice[a][fa] - dice[b][fb]).ge(1).reify();
                wins.push(w);
            }
        }
        m.linear(wins.iter().copied().sum::<IntLinearExp>()).ge(19).post()?;
    }

    let mut out = Out::new();
    out.put("dice", dice);
    Ok(out)
}

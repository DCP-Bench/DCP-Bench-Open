use huub::actions::IntDecisionActions;
use huub::model::expressions::IntLinearExp;
use huub::model::Model;
use huub::solver::{IntLitMeaning, Solver, Status};

fn main() {
    // Four values in 0..=2 whose sum is at least 2; minimise the sum.
    let mut m = Model::default();
    let x = m.new_int_decisions(4, 0..=2);
    let total = m.new_int_decision(0..=8);
    m.linear(x.iter().copied().sum::<IntLinearExp>()).ge(2).post().unwrap();
    m.linear(x.iter().copied().sum::<IntLinearExp>()).eq(total).post().unwrap();

    let (mut solver, map): (Solver, _) = m.lower().to_solver().unwrap();
    let outputs: Vec<_> = x.iter().map(|&v| map.get(&mut solver, v)).collect();
    let objective = map.get(&mut solver, total);

    // Step 1: prove the optimum. This must be the first solve on the solver.
    let best = match solver.solve().minimize(objective) {
        (Status::Complete, Some(best)) => best,
        (status, _) => {
            println!("no proven optimum: {status:?}");
            return;
        }
    };

    // Step 2: pin the objective with an assumption and enumerate over the outputs.
    let pin = objective.lit(&mut solver, IntLitMeaning::Eq(best));
    let mut rows = 0;
    let status = solver
        .solve()
        .assuming(Some(pin))
        .all_solutions(outputs)
        .on_solution(|_| rows += 1)
        .satisfy();
    println!("Optimal value {best}: {rows} solutions ({status:?})");
}

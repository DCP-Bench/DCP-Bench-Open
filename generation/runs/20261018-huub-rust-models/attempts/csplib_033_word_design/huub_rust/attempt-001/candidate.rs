// csplib_033_word_design: find a set S of num_words words of length n over the
// alphabet {A,C,G,T}, encoded 1 for A, 2 for C, 3 for G and 4 for T, such that:
// - Each word in S has 4 symbols from {C,G};
// - Each pair of distinct words in S differ in at least 4 positions; and
// - Each pair of words x and y in S (x and y may be identical) are such that
//   x^R and y^C differ in at least 4 positions, where x^R is the reverse of x and
//   y^C is the Watson-Crick complement of y (A and T swap, C and G swap; with the
//   encoding this is v -> 5 - v).

fn build(inst: &Instance, m: &mut Model) -> Res<Out> {
    let n = inst.size("n");
    let num_words = inst.size("num_words");

    let mut words: Vec<Vec<View<i64>>> = Vec::new();
    for _ in 0..num_words {
        let mut row: Vec<View<i64>> = Vec::new();
        for _ in 0..n {
            row.push(m.new_int_decision(1..=4));
        }
        words.push(row);
    }

    // Each word in S has 4 symbols from {C,G}.
    for w in &words {
        let mut cg: Vec<View<bool>> = Vec::new();
        for &x in w {
            let b = m.contains(Set::from_iter([2i64..=3])).member(x).define();
            cg.push(b);
        }
        m.linear(cg.iter().copied().sum::<IntLinearExp>()).eq(4).post()?;
    }

    // Each pair of distinct words in S differ in at least 4 positions.
    for i in 0..num_words {
        for j in (i + 1)..num_words {
            let mut diff: Vec<View<bool>> = Vec::new();
            for k in 0..n {
                let d = m.linear(words[i][k] - words[j][k]).ne(0).reify();
                diff.push(d);
            }
            m.linear(diff.iter().copied().sum::<IntLinearExp>()).ge(4).post()?;
        }
    }

    // Each pair of words x and y in S (x and y may be identical) are such that
    // x^R and y^C differ in at least 4 positions.
    for x in 0..num_words {
        for y in 0..num_words {
            let mut diff: Vec<View<bool>> = Vec::new();
            for k in 0..n {
                // Position k of x^R is x[n-1-k]; position k of y^C is 5 - y[k].
                // They are equal exactly when the two letters sum to 5.
                let d = m.linear(words[x][n - 1 - k] + words[y][k]).ne(5).reify();
                diff.push(d);
            }
            m.linear(diff.iter().copied().sum::<IntLinearExp>()).ge(4).post()?;
        }
    }

    let mut out = Out::new();
    out.put("words", words);
    Ok(out)
}

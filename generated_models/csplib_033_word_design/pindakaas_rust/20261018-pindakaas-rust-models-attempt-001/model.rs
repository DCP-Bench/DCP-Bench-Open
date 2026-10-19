// Problem csplib_033_word_design (word design over {A,C,G,T}).
// Find num_words words of length n. Letters are encoded 1=A, 2=C, 3=G, 4=T.
// Each word has 4 letters from {C,G}; each pair of distinct words differs in at least 4
// positions; and for every pair x, y (identical allowed) the reverse of x and the
// Watson-Crick complement of y differ in at least 4 positions.
//
// A "same" literal per position is forced true when two letters agree. At most n-4 positions
// may agree, which is the same as at least 4 positions differing.

fn at_most_same(s: &mut Cadical, same: &[Lit], k: i64) -> Res {
    let mut e = LinExp::default();
    for &l in same {
        e += LinExp::from(l);
    }
    post(s, e, Comparator::LessEq, k)
}

fn build(inst: &Instance, s: &mut Cadical) -> Res<Out> {
    let n = inst.size("n");
    let m = inst.size("num_words");

    // words[a][j] is the letter at position j of word a, 1..=4.
    let words: Vec<Vec<IntVar>> = (0..m)
        .map(|_| (0..n).map(|_| IntVar::new(1i64..=4i64)).collect())
        .collect();

    // eq[a][j][v] is the literal "words[a][j] == v + 1" (v is a 0-based letter index).
    let mut eq: Vec<Vec<Vec<Lit>>> = Vec::with_capacity(m);
    for a in 0..m {
        let mut row: Vec<Vec<Lit>> = Vec::with_capacity(n);
        for j in 0..n {
            let mut lits: Vec<Lit> = Vec::with_capacity(4);
            for v in 1..=4i64 {
                let b = words[a][j].equals(s, v)?;
                lits.push(lit_of(s, b)?);
            }
            row.push(lits);
        }
        eq.push(row);
    }

    // Each word has 4 symbols from {C,G}.
    for a in 0..m {
        let mut e = LinExp::default();
        for j in 0..n {
            e += LinExp::from(eq[a][j][1]); // C
            e += LinExp::from(eq[a][j][2]); // G
        }
        post(s, e, Comparator::Equal, 4)?;
    }

    // Each pair of distinct words differs in at least 4 positions.
    for a in 0..m {
        for b in (a + 1)..m {
            let mut same: Vec<Lit> = Vec::with_capacity(n);
            for j in 0..n {
                let l = s.new_lit();
                for v in 0..4 {
                    s.add_clause([!eq[a][j][v], !eq[b][j][v], l])?;
                }
                same.push(l);
            }
            at_most_same(s, &same, n as i64 - 4)?;
        }
    }

    // For every pair x, y (identical allowed), the reverse of x and the Watson-Crick
    // complement of y differ in at least 4 positions.
    // Position j: reverse(x)[j] = x[n-1-j]; complement(y)[j] = 5 - y[j] (A<->T, C<->G).
    for a in 0..m {
        for b in 0..m {
            let mut same: Vec<Lit> = Vec::with_capacity(n);
            for j in 0..n {
                let l = s.new_lit();
                for v in 0..4 {
                    // letter v+1 in x, complement letter 4-v, 0-based index 3-v in y
                    s.add_clause([!eq[a][n - 1 - j][v], !eq[b][j][3 - v], l])?;
                }
                same.push(l);
            }
            at_most_same(s, &same, n as i64 - 4)?;
        }
    }

    let mut out = Out::new();
    out.put("words", &words);
    Ok(out)
}

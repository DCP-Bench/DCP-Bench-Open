csplib_033_word_design plan
find a set S of num_words strings of length n over {A,C,G,T} -> words: IntVar matrix [num_words][n], letters 1..4 (A=1,C=2,G=3,T=4)
each word in S has 4 symbols from {C,G} -> m.among(4, row, {2,3}) per word
each pair of distinct words differ in at least 4 positions -> for each i<j: sum over p of reified (w_i[p] != w_j[p]) >= 4
each pair x,y (identical allowed) has x^R and y^C differing in at least 4 positions -> for each ordered pair (i,j) incl. i=j: sum over p of reified (w_i[n-1-p] + w_j[p] != 5) >= 4 (complement of letter l is 5-l)
objective: none (satisfaction)

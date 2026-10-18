:- lib(ic).
:- lib(ic_global).
:- lib(gfd).
:- lib(listut).
:- lib(branch_and_bound).
:- lib(timeout).

chk(M, N, A) :- ( catch(M:current_predicate(N/A), _, fail) -> printf("%w:%w/%w yes%n", [M,N,A]) ; printf("%w:%w/%w no%n", [M,N,A]) ).

p3 :-
    chk(ic, alldifferent, 1), chk(ic_global, alldifferent, 1), chk(gfd, alldifferent, 1),
    chk(ic, alldistinct, 1), chk(ic_global, alldistinct, 1), chk(gfd, alldistinct, 1),
    chk(ic_global, gcc, 2), chk(ic_global, gcc, 3), chk(gfd, gcc, 2), chk(ic_global, occurrences, 3),
    chk(ic_global, disjunctive, 1), chk(ic_global, cumulative, 2), chk(ic_global, cumulative, 3),
    chk(ic, cumulative, 2), chk(ic, cumulative, 3), chk(ic, disjunctive, 1), chk(ic_global, disjunctive, 2),
    chk(ic, table, 2), chk(ic_global, table, 2), chk(gfd, table, 2), chk(ic_global, table, 3), chk(gfd, table, 3),
    chk(ic, circuit, 1), chk(ic_global, circuit, 1), chk(gfd, circuit, 1), chk(ic_global, lex_le, 2), chk(ic, lex_le, 2),
    chk(ic_global, sorted, 2), chk(ic_global, ordered, 2), chk(gfd, ordered, 2), chk(gfd, sorted, 2),
    chk(ic_global, atmost, 3), chk(gfd, atmost, 3), chk(ic_global, element, 3), chk(ic, element, 3), chk(gfd, element, 3),
    chk(gfd, cumulative, 3), chk(gfd, disjunctive, 1), chk(gfd, sum, 3), chk(ic, sum, 3), chk(ic_global, sum, 3),
    chk(gfd, lex_le, 2), chk(gfd, lex_lt, 2), chk(ic, lex_lt, 2), chk(ic_global, lex_lt, 2),
    chk(ic, '#=', 2), chk(gfd, '#=', 2), chk(ic, '$=', 2),
    chk(ic_global, nvalue, 2), chk(ic_global, count, 4), chk(ic_global, among, 3), chk(ic_global, nvalue, 2),
    chk(ic_global, tuples, 2), chk(ic_global, element, 3), chk(gfd, element, 3),
    chk(ic, dim, 2), chk(ic, multifor, 3), chk(ic, fromto, 3), chk(ic, collection_to_list, 2),
    chk(ic_sets, '#=', 2), chk(fd, '#=', 2), chk(fd, alldifferent, 1), chk(fd, labeling, 1),
    chk(ic, labeling, 1), chk(ic, search, 6), chk(gfd, search, 6), chk(ic, bb_min, 3), chk(ic, minimize, 2),
    chk(gfd, minimize, 2), chk(branch_and_bound, bb_min, 3), chk(timeout, timeout, 3), chk(ic, timeout, 3),
    chk(gfd, '#<=>', 2), chk(ic, '#<=>', 2), chk(ic, '#==>', 2), chk(ic, '#\\/', 2), chk(gfd, '#\\/', 2),
    chk(ic, '#\\=', 2), chk(gfd, '#\\=', 2), chk(ic, '<=>', 2), chk(gfd, '<=>', 2), chk(gfd, '=>', 2),
    chk(ic, get_var_bounds, 3), chk(gfd, get_var_bounds, 3), chk(ic, get_domain_as_list, 2), chk(ic, fd_dom, 2), chk(gfd, fd_dom, 2),
    chk(ic, indomain, 1), chk(gfd, indomain, 1), chk(ic, indomain, 2), chk(ic, labeling, 2), chk(gfd, labeling, 2),
    chk(ic_global, dim, 2), chk(ic, fd_var, 1), chk(ic, dvar_domain, 2), chk(ic, is_suspension, 1),
    chk(listut, nth0, 3), chk(lists, nth0, 3), chk(lists, nth1, 3), chk(listut, nth1, 3),
    chk(ic, '$=', 2), chk(ic, '#<', 2), chk(ic, '#>', 2),
    chk(ic, reified_all_different, 2), chk(ic, sumr, 3), chk(ic, ic_linear, 2),
    chk(ic, cumulative, 4), chk(ic, not_in_cumulative, 3), chk(ic, is_in, 2),
    chk(ic, tuples_in, 2), chk(ic_global, tuples_in, 2), chk(gfd, tuples_in, 2),
    chk(ic, table_lex, 2), chk(ic, element_, 3).

:- p3, halt.
:- halt.

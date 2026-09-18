/* A MiniZinc grammar for highlight.js, which ships none.
 *
 * Deliberately small: it colours what a reader scans a model for — the
 * declarations, the constraints, the solve item — and leaves the rest plain.
 * Anything it does not know stays unhighlighted rather than being coloured as
 * the wrong kind of token.
 *
 * Keywords follow the MiniZinc 2.8 specification. `built_in` lists the standard
 * functions and the globals from solvers/minizinc_gecode's skill; adding a
 * global here is a one-word change.
 */
(function () {
  if (!window.hljs) return;

  hljs.registerLanguage('minizinc', function (hljs) {
    return {
      name: 'MiniZinc',
      aliases: ['mzn'],
      case_insensitive: false,
      keywords: {
        keyword:
          'annotation any array bool case constraint diff div else elseif endif ' +
          'enum float function if in include int intersect let list maximize ' +
          'minimize mod not of op opt output par predicate record satisfy set ' +
          'solve string subset superset symdiff test then tuple type union var ' +
          'where xor',
        literal: 'true false',
        built_in:
          // Standard library.
          'abs arg_max arg_min array1d array2d array3d array4d array5d bool2int ' +
          'card ceil concat dom dom_array exists floor forall index_set ' +
          'index_set_1of2 index_set_2of2 join length ln log log2 log10 max min ' +
          'pow product round show show_float show_int sqrt sum trace ' +
          // Globals.
          'all_different alldifferent all_equal among at_least at_most ' +
          'bin_packing circuit count cumulative decreasing diffn disjunctive ' +
          'element global_cardinality increasing inverse lex_less lex_lesseq ' +
          'network_flow nvalue regular sort subcircuit table value_precede',
      },
      contains: [
        hljs.COMMENT('%', '$'),
        hljs.C_BLOCK_COMMENT_MODE,
        // Strings carry \( ) interpolation, which is most of an output item.
        {
          className: 'string',
          begin: '"',
          end: '"',
          illegal: '\\n',
          contains: [
            hljs.BACKSLASH_ESCAPE,
            { className: 'subst', begin: '\\\\\\(', end: '\\)', keywords: 'show' },
          ],
        },
        // 1..n, 0o17 and 0xff, before the general number rule.
        { className: 'number', begin: '\\b0[xX][0-9a-fA-F]+\\b' },
        { className: 'number', begin: '\\b0[oO][0-7]+\\b' },
        { className: 'number', begin: '\\b\\d+\\.\\d+([eE][-+]?\\d+)?\\b' },
        { className: 'number', begin: '\\b\\d+\\b' },
        // :: solver annotations, e.g. :: int_search(...).
        { className: 'meta', begin: '::\\s*[a-zA-Z_][a-zA-Z0-9_]*' },
        // The logical operators a constraint is read by.
        { className: 'operator', begin: '/\\\\|\\\\/|<->|->|<-|\\+\\+|\\.\\.|[<>!=]=|[<>=]' },
      ],
    };
  });
})();

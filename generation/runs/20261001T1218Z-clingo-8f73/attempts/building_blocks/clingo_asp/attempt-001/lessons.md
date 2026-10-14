# building_blocks with clingo_asp

The instance fields `alphabet` and `words_str` are strings, so the runner emits
`alphabet("ABC...")` and `words_str(0,"BAKE")`. Clingo's term language has no string
operation (no length, no character access, no concatenation), so a pure ASP program cannot
turn a word into letter numbers. The only route is an embedded script. This attempt used
`#script (lua)`; the image answers `lua support not available` (see evaluation.json,
`detail`). `#script (python)` is unavailable too, as the clingo-asp skill already says.

Pair is a blocker candidate: the framework as installed cannot express the required construct.

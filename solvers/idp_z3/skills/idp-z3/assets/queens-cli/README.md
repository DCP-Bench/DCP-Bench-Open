# Six queens (satisfy, all solutions, command line)

**Problem:** Place 6 queens on a 6x6 board so that no two attack each other; list every placement.
**Shows:** a complete `.idp` file (named `vocabulary`, `theory`, `structure` blocks and a `procedure main`) run with the `idp-engine` command; a type declared `<: Int` and sized in the structure; `model_expand(..., max=0, timeout_seconds=0)` for all models; the closing `No more models.` that proves the list is complete.
**Run:** `idp-engine --no-timing queens.idp`
**Expected:** `Model 4`
**Expected:** `No more models.`

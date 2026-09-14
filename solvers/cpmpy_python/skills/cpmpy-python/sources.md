# Sources for `cpmpy-python`

Documentation this skill's instructions were written from. Add an entry
whenever a claim here comes from a specific page or version.

- <https://cpmpy.readthedocs.io/> — CPMpy documentation, accessed 2026-09-10
- <https://github.com/CPMpy/cpmpy> — CPMpy 1.0.0, the version in the integration image

The API tables and every "verified" gotcha were checked directly against
CPMpy 1.0.0 as installed in this repository's environment, not taken from
documentation alone:

- Every listed name resolves in the `cpmpy` namespace at 1.0.0.
- `cp.Cumulative` and `cp.NoOverlap` take `end` as optional at 1.0.0, so the
  signatures here follow the installed code rather than older examples.
- Built-in `max`, `min`, `any` and `all` raise
  `ValueError: __bool__ should not be called on a CPMPy expression`; built-in
  `sum` does not and yields the same expression as `cp.sum`.
- A float coefficient raises
  `TypeError: Multiplication does not support float constants`.
- Rank-2 by rank-1 multiplication broadcasts as NumPy does, and a mismatched
  shape raises `ValueError` rather than misaligning silently. An earlier
  in-house prompt warned that this was unreliable; that does not reproduce on
  1.0.0, so the warning is deliberately not repeated here.

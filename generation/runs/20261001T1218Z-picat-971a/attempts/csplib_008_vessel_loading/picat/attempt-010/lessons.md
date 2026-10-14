# Lesson (picat integration)

`Data.get(length)` with the atom written out returns 2, not the field `length`
(the instance's `length` is `[1,4,4]`). Measured in attempts 007 and 008 of
csplib_008_vessel_loading: `Data.get('length')` also returns 2, while
`Key = 'length', Data.get(Key)` and a lookup through `Data.to_list()` return the list.
The symptom with the literal atom is `error(type_error(compound,2),index_operator [])`
at the first `Lengths[I]`. Other keys (`width`, `deck_width`, `classes`) were read
correctly. Workaround: bind the key to a variable first.
Evidence: generation/runs/20261001T1218Z-picat-971a/attempts/csplib_008_vessel_loading/picat/attempt-008/evaluation.json

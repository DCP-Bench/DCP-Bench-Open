attempt-002 replaces Sum(x) >= 1 over a single term (an audience reached by one medium) with is_selected[m] == 1. The attempt-001 form crashed on json:4 with runner status error 'SystemExit: 1' and empty stderr; the other instances were fine.
Single-term Sum over one Boolean inside satisfy() seems to be the trigger; not confirmed on a minimal case.

# Negative-control baseline: executable but intentionally non-matching.
import json
print(json.dumps({'__ml_research_loop_nonexistent_var__': 0}))
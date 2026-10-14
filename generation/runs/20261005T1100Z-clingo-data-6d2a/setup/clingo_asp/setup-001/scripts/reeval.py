"""Re-evaluate a sample of retained clingo_asp models with the rebuilt image."""
import glob, json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(r"C:\Users\kostis\code\DCP-Bench-Open")
OUT = Path(sys.argv[1])
STRINGS = ["cabling", "facility_location", "room_assignment", "session2_movie_scheduling", "who_killed_agatha"]
CAPS = ["covering_opl", "csplib_018_water_bucket", "csplib_023_magic_hexagon", "csplib_050_diamond_free",
        "csplib_067_quasigroup_completion", "minesweeper", "n_puzzle", "session2_subsets_100", "set_game"]
NAMES_NOTES = ["csplib_054_n_queens", "jobs_puzzle", "clock_triplets", "initials_queue", "abbots_puzzle", "allergy"]


def run(model):
    problem = Path(model).parts[-4]
    cmd = [str(REPO / ".venv/Scripts/python.exe"), "-W", "ignore", "-m", "evaluation.check", model,
           "--problem", problem, "--solver", "clingo_asp", "--instance-count", "99", "--solution-limit", "2",
           "--execution-timeout", "180", "--reference-timeout", "180"]
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    name = Path(model).parts[-2]
    (OUT / f"{problem}__{name}.json").write_text(p.stdout + "\n--- stderr ---\n" + p.stderr[-4000:], encoding="utf-8")
    try:
        r = json.loads(p.stdout)
        return model, r.get("accepted"), r.get("reason"), r.get("instances_checked"), r.get("instances_available")
    except Exception:
        return model, None, f"unparsed exit {p.returncode}", None, None


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    models = []
    for problem in STRINGS + CAPS + NAMES_NOTES:
        models += sorted(glob.glob(str(REPO / "generated_models" / problem / "clingo_asp" / "*" / "model.lp")))
    with ThreadPoolExecutor(4) as pool:
        rows = list(pool.map(run, models))
    for row in rows:
        print(json.dumps([str(Path(row[0]).relative_to(REPO)).replace("\\", "/"), *row[1:]]))

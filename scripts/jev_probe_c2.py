#!/usr/bin/env python3
"""C2: does a plausible, in-world-consistent price table move `fair` off 0.10?"""
import json, os, urllib.request

URL = "https://api.typesafe.ai/v1/systemone"
KEY = os.environ["TYPESAFE_API_KEY"]
PRICES = {"a loaf of bread": "2 copper coins", "a night at an inn": "5 copper coins",
          "a sword": "40 copper coins", "a house": "1200 copper coins"}
Q = {
    "unfair": {"type": "noul",
        "instructions": "The reward offered is unfairly low for the danger and labor the job requires."},
    "fair": {"type": "noul",
        "instructions": "The reward offered is appropriate for the danger and labor the job requires."},
}

def ask(state):
    body = json.dumps({"state": state, "model": "jev-latest", "questions": Q}).encode()
    req = urllib.request.Request(URL, data=body, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

out = {}
for n, note in [(3, "1.5 loaves"), (40, "a sword"), (300, "quarter house"),
                (1200, "1 house"), (3000, "2.5 houses"), (12000, "10 houses")]:
    st = {"quest": "Clear out a goblin warren", "reward": f"{n} copper coins",
          "danger": "Fighters have died taking this job",
          "local_prices": PRICES}
    a = ask(st)["answers"]
    out[f"C2/table/{n}cu"] = {"note": note} | {k: round(v["noul"], 4) for k, v in a.items()}
    print(f"{n:6}cu ({note:14}) {out[f'C2/table/{n}cu']}", flush=True)

json.dump(out, open("jev_results_c2.json", "w"), indent=1, ensure_ascii=False)

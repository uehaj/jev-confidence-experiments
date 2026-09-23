#!/usr/bin/env python3
"""Probe jev-1.13 for quantitative ("相場") sense vs. commonsense judgment."""
import json, os, urllib.request, sys

URL = "https://api.typesafe.ai/v1/systemone"
KEY = os.environ["TYPESAFE_API_KEY"]

Q_EN = {
    "unfair": {"type": "noul",
        "instructions": "The reward offered is unfairly low for the danger and labor the job requires."},
    "fair": {"type": "noul",
        "instructions": "The reward offered is appropriate for the danger and labor the job requires."},
}
Q_JA = {
    "unfair": {"type": "noul",
        "instructions": "提示された報酬は、この仕事が要求する危険と労働に対して不当に低い。"},
    "fair": {"type": "noul",
        "instructions": "提示された報酬は、この仕事が要求する危険と労働に対して妥当である。"},
}

def ask(state, questions):
    body = json.dumps({"state": state, "model": "jev-latest", "questions": questions}).encode()
    req = urllib.request.Request(URL, data=body, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def quest_en(reward, **extra):
    return dict({"quest": "Clear out a goblin warren", "reward": reward,
                 "danger": "Fighters have died taking this job"}, **extra)

def quest_ja(reward, **extra):
    return dict({"依頼": "ゴブリンの群れの討伐", "報酬": reward,
                 "危険度": "死者が出うる"}, **extra)

CELLS = []
# A: count ladder, denomination fixed (EN)
for n in [1, 3, 30, 300, 3000, 30000]:
    CELLS.append((f"A/count/{n}cu", quest_en(f"{n} copper coins"), Q_EN))
# B: denomination ladder, count fixed at 3 (EN)
for d in ["copper", "silver", "gold", "platinum"]:
    CELLS.append((f"B/denom/3{d}", quest_en(f"3 {d} coins"), Q_EN))
# C: state override of the in-world exchange rate
CELLS.append(("C/override/house", quest_en("3 copper coins",
    economy="In this realm, one copper coin buys a house."), Q_EN))
CELLS.append(("C/override/bread", quest_en("3 copper coins",
    economy="In this realm, one copper coin buys a loaf of bread."), Q_EN))
# D: determinism (repeats of two A cells)
for i in (2, 3):
    CELLS.append((f"D/repeat/3cu#{i}", quest_en("3 copper coins"), Q_EN))
    CELLS.append((f"D/repeat/3000cu#{i}", quest_en("3000 copper coins"), Q_EN))
# E: Japanese replicate of A
for n in [1, 3, 30, 300, 3000, 30000]:
    CELLS.append((f"E/ja/count/{n}", quest_ja(f"銅貨{n}枚"), Q_JA))
# F: real-world domain where a 相場 exists in training data
for pay in ["$1,000", "$50,000", "$150,000", "$5,000,000"]:
    CELLS.append((f"F/salary/{pay}", {
        "job": "Full-time senior software engineer in San Francisco, 40 hours a week",
        "offer": f"{pay} per year"}, {
        "unfair": {"type": "noul", "instructions": "The pay offered is unfairly low for this job."},
        "fair": {"type": "noul", "instructions": "The pay offered is appropriate for this job."},
    }))

out = {}
for name, state, qs in CELLS:
    r = ask(state, qs)
    out[name] = {k: round(v["noul"], 4) for k, v in r["answers"].items()} \
        if "answers" in r else r
    print(f"{name:26} {out[name]}", flush=True)

path = os.path.join(os.path.dirname(__file__), "jev_results.json")
json.dump(out, open(path, "w"), indent=1, ensure_ascii=False)
print("wrote", path)

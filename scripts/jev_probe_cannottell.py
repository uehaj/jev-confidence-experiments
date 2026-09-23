#!/usr/bin/env python3
"""Controlled A/B: does adding a 'cannot tell' option convert confident-wrong into confident-unknown?
Identical state, identical instructions. Only the option set differs."""
import json, os, urllib.request
URL="https://api.typesafe.ai/v1/systemone"; KEY=os.environ["TYPESAFE_API_KEY"]
def ask(state, questions):
    b=json.dumps({"state":state,"model":"jev-latest","questions":questions}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))["answers"]

PAY_OPTS={"below_market":"The offer is below the going rate",
          "at_market":"The offer is around the going rate",
          "above_market":"The offer is above the going rate"}
PAY_INSTR="Compared with the going rate for this job, how does the offered pay compare?"
CI_OPTS={"flaky_infra":"Infrastructure or test flakiness, not a code defect",
         "real_regression":"A code change broke behaviour that used to work",
         "config_error":"A misconfiguration in the pipeline or environment"}
CI_INSTR="What is the most likely cause of this CI failure?"

CASES=[
 ("PAY/minimal/without", {"offer":"$150,000 per year"}, PAY_INSTR, PAY_OPTS),
 ("PAY/minimal/with",    {"offer":"$150,000 per year"}, PAY_INSTR,
    PAY_OPTS|{"cannot_tell":"The information given does not say what job this is, so the comparison cannot be made"}),
 ("CI/minimal/without",  {"job":"unit-tests","log":"CI failed."}, CI_INSTR, CI_OPTS),
 ("CI/minimal/with",     {"job":"unit-tests","log":"CI failed."}, CI_INSTR,
    CI_OPTS|{"cannot_tell":"The information given does not identify a cause"}),
]
out={}
for name, st, instr, opts in CASES:
    a=ask(st, {"q":{"type":"choice","instructions":instr,"criteria":opts}})["q"]
    out[name]={"choice":a["choice"],"confidence":round(a["confidence"],3),
               "probabilities":{k:round(v,3) for k,v in a["probabilities"].items()}}
    print(f"{name:22} -> {a['choice']:16} conf={a['confidence']:.3f}  {out[name]['probabilities']}",flush=True)
json.dump(out,open("jev_results_cannottell.json","w"),indent=1,ensure_ascii=False)

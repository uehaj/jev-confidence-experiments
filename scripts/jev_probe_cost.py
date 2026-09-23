#!/usr/bin/env python3
"""Does adding cannot_tell blunt the answer when the material IS sufficient?"""
import json, os, urllib.request
URL="https://api.typesafe.ai/v1/systemone"; KEY=os.environ["TYPESAFE_API_KEY"]
def ask(state, criteria, instr):
    q={"q":{"type":"choice","instructions":instr,"criteria":criteria}}
    b=json.dumps({"state":state,"model":"jev-latest","questions":q}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))["answers"]["q"]
def show(name,v):
    p={k:round(x,3) for k,x in v["probabilities"].items()}
    print(f"{name:30} {v['choice']:16} conf={v['confidence']:.3f}  {p}",flush=True)
    return {"choice":v["choice"],"confidence":round(v["confidence"],3),"probabilities":p}

DIFF=("+def compute_refund(amount, proration_days):\n"
      "+    unused = amount * 0\n"
      "+    return round(amount * proration_days / 30)\n")
REV3={"auto_fix":"Apply the suggested change without a person looking at it",
      "human_review":"A person should decide before anything changes",
      "dismiss":"The finding is not correct or not worth acting on"}
REV4=REV3|{"cannot_tell":"The information given does not say what this project's conventions are, so the right handling cannot be chosen"}
REV_Q="How should this automated review finding be handled?"
REV_ST={"diff":DIFF,"finding":"`unused` is assigned but never read. Remove it."}

CI_ST={"job":"unit-tests","log":("FAIL tests/billing/test_invoice.py::test_prorated_refund\n"
  "  assert refund == 1250\n  E  assert 0 == 1250\n"
  "  tests/billing/test_invoice.py:88: AssertionError\n  billing/invoice.py:142 in compute_refund"),
  "changed_files":["billing/invoice.py","billing/schedule.py"],"branch":"feat/annual-plans"}
CI3={"flaky_infra":"Infrastructure or test flakiness, not a code defect",
     "real_regression":"A code change broke behaviour that used to work",
     "config_error":"A misconfiguration in the pipeline or environment"}
CI4=CI3|{"cannot_tell":"The information given does not identify a cause"}
CI_Q="What is the most likely cause of this CI failure?"

res={}
res["review_obvious/3択(既測)"]=show("review_obvious/3択", ask(REV_ST,REV3,REV_Q))
res["review_obvious/4択(+ct)"]=show("review_obvious/4択(+ct)", ask(REV_ST,REV4,REV_Q))
res["ci_fulllog/4択(既測)"]=show("ci_fulllog/4択", ask(CI_ST,CI4,CI_Q))
res["ci_fulllog/3択(-ct)"]=show("ci_fulllog/3択(-ct)", ask(CI_ST,CI3,CI_Q))
json.dump(res,open("jev_results_cost.json","w"),indent=1,ensure_ascii=False)

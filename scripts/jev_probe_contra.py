#!/usr/bin/env python3
"""C1: a genuinely self-contradictory state.  C2: same history as numbers vs as a sentence."""
import json, os, urllib.request
URL="https://api.typesafe.ai/v1/systemone"; KEY=os.environ["TYPESAFE_API_KEY"]
Q={
 "cause":{"type":"choice","instructions":"What is the most likely cause of this CI failure?",
   "criteria":{"flaky_infra":"Infrastructure or test flakiness, not a code defect",
               "real_regression":"A code change broke behaviour that used to work",
               "config_error":"A misconfiguration in the pipeline or environment",
               "cannot_tell":"The information given does not identify a cause"}},
 "enough_info":{"type":"noul","instructions":"The information given is sufficient to identify which change caused this failure."},
}
BASE={"job":"unit-tests","log":("FAIL tests/billing/test_invoice.py::test_prorated_refund\n"
  "  assert refund == 1250\n  E  assert 0 == 1250\n"
  "  tests/billing/test_invoice.py:88: AssertionError\n  billing/invoice.py:142 in compute_refund"),
  "changed_files":["billing/invoice.py","billing/schedule.py"],"branch":"feat/annual-plans"}
A="This test passed on every run before commit 4f1a2c and has failed on every run since. That commit modified billing/invoice.py."
B="This test has failed on 2 of the last 10 runs. All 10 runs were on commit 4f1a2c, and 8 of them passed."
NUMERIC=[{"commit":"9b3e1a","result":"pass"},{"commit":"9b3e1a","result":"pass"},
         {"commit":"9b3e1a","result":"pass"},{"commit":"4f1a2c","result":"fail"},
         {"commit":"4f1a2c","result":"fail"},{"commit":"4f1a2c","result":"fail"},
         {"commit":"4f1a2c","result":"fail"}]
def ask(st):
    b=json.dumps({"state":st,"model":"jev-latest","questions":Q}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))
out={}
def run(name, st):
    d=ask(st); a=d["answers"]; c=a["cause"]
    out[name]={"model":d.get("model"),"choice":c["choice"],"confidence":round(c["confidence"],3),
               "probabilities":{k:round(v,3) for k,v in c["probabilities"].items()},
               "enough_info":round(a["enough_info"]["noul"],3)}
    print(f"{name:22} {c['choice']:16} conf={c['confidence']:.3f} enough={out[name]['enough_info']:.2f} "
          f"{out[name]['probabilities']}  model={d.get('model')}",flush=True)
run("C1/history_A_only",      BASE|{"history":A})
run("C1/history_B_only",      BASE|{"history":B})
run("C1/contradiction_A_and_B", BASE|{"history":A+" "+B})
run("C2/history_as_numbers",  BASE|{"recent_runs":NUMERIC,"changed_files_in_4f1a2c":["billing/invoice.py"]})
run("C2/history_as_words",    BASE|{"history":A})
json.dump(out,open("jev_results_contra.json","w"),indent=1,ensure_ascii=False)

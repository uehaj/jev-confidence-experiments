#!/usr/bin/env python3
"""C3: is C's failure due to implausibility, or to one hop of unit conversion?"""
import json, os, urllib.request
URL="https://api.typesafe.ai/v1/systemone"; KEY=os.environ["TYPESAFE_API_KEY"]
Q={"unfair":{"type":"noul","instructions":"The reward offered is unfairly low for the danger and labor the job requires."},
   "fair":{"type":"noul","instructions":"The reward offered is appropriate for the danger and labor the job requires."}}
def ask(st):
    b=json.dumps({"state":st,"model":"jev-latest","questions":Q}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))["answers"]
base={"quest":"Clear out a goblin warren","danger":"Fighters have died taking this job"}
CELLS={
 # extreme + same-unit/direct  -> moves => indirection was the cause
 "C3/extreme_direct": base|{"reward":"3 copper coins","local_prices":{"a house":"1 copper coin"}},
 # plausible + indirect (reward stated in houses, price table in coins)
 "C3/plausible_indirect": base|{"reward":"a purse of copper coins worth two and a half houses",
                                "local_prices":{"a loaf of bread":"2 copper coins","a house":"1200 copper coins"}},
 # extreme + same-unit, larger gap (control for the 3-vs-1 tightness)
 "C3/extreme_direct_x1000": base|{"reward":"3000 copper coins","local_prices":{"a house":"1 copper coin"}},
}
out={}
for k,st in CELLS.items():
    out[k]={n:round(v["noul"],4) for n,v in ask(st).items()}
    print(f"{k:28} {out[k]}",flush=True)
json.dump(out,open("jev_results_c3.json","w"),indent=1,ensure_ascii=False)

#!/usr/bin/env python3
"""C5: magnitude-only contrast, integers throughout, identical wording and value."""
import json, os, urllib.request
URL="https://api.typesafe.ai/v1/systemone"; KEY=os.environ["TYPESAFE_API_KEY"]
Q={"unfair":{"type":"noul","instructions":"The reward offered is unfairly low for the danger and labor the job requires."},
   "fair":{"type":"noul","instructions":"The reward offered is appropriate for the danger and labor the job requires."}}
def ask(st):
    b=json.dumps({"state":st,"model":"jev-latest","questions":Q}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))["answers"]
base={"quest":"Clear out a goblin warren","danger":"Fighters have died taking this job"}
out={}
# Same wording, same purchasing power (2.5 houses), integers only. Only the scale of the numbers differs.
for house, reward in [(12, 30), (1200, 3000), (120000, 300000)]:
    k=f"C5/house{house}"
    st=base|{"reward":f"{reward} copper coins (worth about two and a half houses)",
             "local_prices":{"a house":f"{house} copper coins"}}
    out[k]={n:round(v["noul"],4) for n,v in ask(st).items()}
    print(f"{k:16} reward={reward:7} {out[k]}",flush=True)
json.dump(out,open("jev_results_c5.json","w"),indent=1,ensure_ascii=False)

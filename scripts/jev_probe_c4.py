#!/usr/bin/env python3
"""C4: when a numeral and a verbal value description coexist, which wins?"""
import json, os, urllib.request
URL="https://api.typesafe.ai/v1/systemone"; KEY=os.environ["TYPESAFE_API_KEY"]
Q={"unfair":{"type":"noul","instructions":"The reward offered is unfairly low for the danger and labor the job requires."},
   "fair":{"type":"noul","instructions":"The reward offered is appropriate for the danger and labor the job requires."}}
def ask(st):
    b=json.dumps({"state":st,"model":"jev-latest","questions":Q}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))["answers"]
base={"quest":"Clear out a goblin warren","danger":"Fighters have died taking this job"}
# All three cells describe the SAME purchasing power: about two and a half houses.
CELLS={
 # big numeral + verbal value, internally consistent
 "C4/numeral3000+words": base|{"reward":"3000 copper coins (worth about two and a half houses)",
   "local_prices":{"a loaf of bread":"2 copper coins","a house":"1200 copper coins"}},
 # small numeral + same verbal value, internally consistent (coins are simply worth more here)
 "C4/numeral3+words": base|{"reward":"3 copper coins (worth about two and a half houses)",
   "local_prices":{"a loaf of bread":"0.002 copper coins","a house":"1.2 copper coins"}},
 # no numeral at all, same tiny-coin world (control for the world's scale itself)
 "C4/nonumeral_tinyworld": base|{"reward":"a purse of copper coins worth about two and a half houses",
   "local_prices":{"a loaf of bread":"0.002 copper coins","a house":"1.2 copper coins"}},
}
out={}
for k,st in CELLS.items():
    out[k]={n:round(v["noul"],4) for n,v in ask(st).items()}
    print(f"{k:26} {out[k]}",flush=True)
json.dump(out,open("jev_results_c4.json","w"),indent=1,ensure_ascii=False)

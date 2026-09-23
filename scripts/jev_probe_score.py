#!/usr/bin/env python3
"""Does the disclosed confidence formula hold for Score? Isolate the number of levels."""
import json, os, urllib.request
URL="https://api.typesafe.ai/v1/systemone"; KEY=os.environ["TYPESAFE_API_KEY"]
ST={"role":"senior software engineer","location":"San Francisco, CA","hours":"40 per week",
    "experience":"8 years","company":"a 300-person B2B SaaS company","offer":"$150,000 per year"}
INSTR="How appropriate is the offered pay for this job?"
LEVELS={
 3:["clearly low","about right","clearly generous"],
 4:["insultingly low","clearly low","about right","clearly generous"],
 5:["insultingly low","clearly low","about right","clearly generous","extravagant"],
 6:["insultingly low","clearly low","slightly low","about right","clearly generous","extravagant"],
}
def ask(levels):
    q={"q":{"type":"score","instructions":INSTR,"criteria":levels}}
    b=json.dumps({"state":ST,"model":"jev-latest","questions":q}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))["answers"]["q"]
res={}
for n,lv in LEVELS.items():
    v=ask(lv); p=v["probabilities"]
    vals=[p[str(i)] for i in range(n)] if isinstance(p,dict) else list(p)
    peak=max(vals); f=(n*peak-1)/(n-1)
    res[f"score_{n}levels"]={"probabilities":[round(x,3) for x in vals],
        "confidence":round(v["confidence"],3),"formula":round(f,3),
        "diff":round(v["confidence"]-f,3),"score":round(v["score"],2)}
    print(f"{n}段階  conf={v['confidence']:.3f}  式={f:.3f}  差={v['confidence']-f:+.3f}   "
          f"p={[round(x,2) for x in vals]}",flush=True)
json.dump(res,open("jev_results_score.json","w"),indent=1,ensure_ascii=False)

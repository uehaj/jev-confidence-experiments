#!/usr/bin/env python3
"""G: is `confidence` a second, independent axis, or a statistic of `probabilities`?"""
import json, os, math, urllib.request
URL="https://api.typesafe.ai/v1/systemone"; KEY=os.environ["TYPESAFE_API_KEY"]
OPTS=["below_market","at_market","above_market"]
Q={
 "level":{"type":"choice","instructions":"Compared with the going rate for this job, how does the offered pay compare?",
   "criteria":{"below_market":"The offer is below the going rate",
               "at_market":"The offer is around the going rate",
               "above_market":"The offer is above the going rate"}},
 "appropriate":{"type":"score","instructions":"How appropriate is the offered pay for this job?",
   "criteria":["insultingly low","clearly low","about right","clearly generous","extravagant"]},
}
def ask(st):
    b=json.dumps({"state":st,"model":"jev-latest","questions":Q}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))["answers"]

FULL={"role":"senior software engineer","location":"San Francisco, CA","hours":"40 per week",
      "experience":"8 years","company":"a 300-person B2B SaaS company","offer":"$150,000 per year"}
CELLS={
 "G/full":    FULL,
 "G/partial": {k:FULL[k] for k in ("role","offer")},          # location/hours/experience 削除
 "G/minimal": {"offer":"$150,000 per year"},                   # 額だけ
 "G/obvious": FULL|{"offer":"$8,000 per year"},                # 誰も割れない案件（対照）
}
def peak_conf(p): n=len(p); m=max(p); return (n*m-1)/(n-1)

out={}
for k,st in CELLS.items():
    a=ask(st)
    row={}
    for qid in ("level","appropriate"):
        ans=a[qid]
        pr=ans["probabilities"]
        vals=list(pr.values()) if isinstance(pr,dict) else list(pr)
        row[qid]={"probabilities":[round(v,4) for v in vals],
                  "confidence":round(ans["confidence"],4),
                  "peak_formula":round(peak_conf(vals),4),
                  "answer":ans.get("choice", ans.get("score"))}
    out[k]=row
    print(k)
    for qid,r in row.items():
        print(f"   {qid:12} ans={r['answer']!s:14} conf={r['confidence']:.3f}  "
              f"peak={r['peak_formula']:.3f}  p={r['probabilities']}")
json.dump(out,open("jev_results_conf.json","w"),indent=1,ensure_ascii=False)

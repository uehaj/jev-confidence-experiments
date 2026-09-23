#!/usr/bin/env python3
"""[A] does cannot_tell absorb 'essentially split' cases?  [B] does the disclosed formula hold for n=4?"""
import json, os, urllib.request
URL="https://api.typesafe.ai/v1/systemone"; KEY=os.environ["TYPESAFE_API_KEY"]
def ask(state, questions):
    b=json.dumps({"state":state,"model":"jev-latest","questions":questions}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))["answers"]
def show(name,a,qid="q"):
    v=a[qid]; p=v["probabilities"]; n=len(p); peak=max(p.values())
    f=(n*peak-1)/(n-1)
    out={"choice":v["choice"],"confidence":round(v["confidence"],3),"n":n,
         "peak":round(peak,3),"formula":round(f,3),
         "probabilities":{k:round(x,3) for k,x in p.items()}}
    print(f"{name:26} {v['choice']:16} conf={v['confidence']:.3f} 式={f:.3f}  {out['probabilities']}",flush=True)
    return out

res={}
# ---- [A] 型2（安定して低い）に cannot_tell を足す ----
MON_LINE="2026-09-22T03:14:07Z ERROR payments.worker: retry 3/3 failed for charge ch_9f21: upstream returned 503"
MON3={"ignore":"No action needed","ticket":"File a ticket for someone to look at during working hours",
      "page":"Wake someone up now"}
MON4=MON3|{"cannot_tell":"The information given does not say how important this service is or what the on-call policy is, so the right action cannot be chosen"}
for i in (1,2):
    res[f"A/monitor/cannot_tell#{i}"]=show(f"A/monitor/cannot_tell#{i}",
        ask({"line":MON_LINE},{"q":{"type":"choice",
            "instructions":"What should be done about this log line?","criteria":MON4}}))

DIFF=("+def compute_refund(amount, proration_days):\n"
      "+    unused = amount * 0\n"
      "+    return round(amount * proration_days / 30)\n")
REV4={"auto_fix":"Apply the suggested change without a person looking at it",
      "human_review":"A person should decide before anything changes",
      "dismiss":"The finding is not correct or not worth acting on",
      "cannot_tell":"The information given does not say what this project's conventions are, so the right handling cannot be chosen"}
res["A/review/cannot_tell"]=show("A/review/cannot_tell",
    ask({"diff":DIFF,"finding":"`compute_refund` should be named `calculate_refund_amount` for consistency with the rest of the module."},
        {"q":{"type":"choice","instructions":"How should this automated review finding be handled?","criteria":REV4}}))

# ---- [B] n=4 で開示式が成り立つか ----
res["B/ci_cause_n4"]=show("B/ci_cause_n4", ask(
  {"job":"unit-tests","log":("FAIL tests/billing/test_invoice.py::test_prorated_refund\n"
    "  assert refund == 1250\n  E  assert 0 == 1250\n"
    "  tests/billing/test_invoice.py:88: AssertionError\n  billing/invoice.py:142 in compute_refund"),
   "changed_files":["billing/invoice.py","billing/schedule.py"],"branch":"feat/annual-plans"},
  {"q":{"type":"choice","instructions":"What is the most likely cause of this CI failure?",
    "criteria":{"flaky_infra":"Infrastructure or test flakiness, not a code defect",
                "real_regression":"A code change broke behaviour that used to work",
                "config_error":"A misconfiguration in the pipeline or environment",
                "cannot_tell":"The information given does not identify a cause"}}}))

res["B/issue_team_n4"]=show("B/issue_team_n4", ask(
  {"タイトル":"経費精算画面で申請ボタンが押せない",
   "本文":"経費精算画面で申請ボタンが押せません。困っています。"},
  {"q":{"type":"choice","instructions":"この報告はどのチームが対応すべきか。",
    "criteria":{"infra":"サーバ・ネットワーク・基盤の問題","app":"アプリケーションの不具合",
                "account":"権限・アカウント設定の問題","cannot_tell":"報告された内容では判断できない"}}}))

json.dump(res,open("jev_results_split.json","w"),indent=1,ensure_ascii=False)

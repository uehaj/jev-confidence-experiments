#!/usr/bin/env python3
"""Ops-domain probes: CI failures, internal issues, loop control, review triage, log monitoring."""
import json, os, urllib.request
URL="https://api.typesafe.ai/v1/systemone"; KEY=os.environ["TYPESAFE_API_KEY"]

def ask(state, questions):
    b=json.dumps({"state":state,"model":"jev-latest","questions":questions}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))["answers"]

def fmt(a):
    out={}
    for k,v in a.items():
        if v["type"]=="noul": out[k]=round(v["noul"],3)
        elif v["type"]=="choice": out[k]=(v["choice"], round(v["confidence"],3))
        else: out[k]=(round(v["score"],2), round(v["confidence"],3))
    return out

results={}
def run(name, state, questions):
    results[name]=fmt(ask(state,questions))
    print(f"{name:34} {results[name]}", flush=True)

# ---------- Case 1: CI failure dispatch ----------
Q_CI={
 "cause":{"type":"choice","instructions":"What is the most likely cause of this CI failure?",
   "criteria":{"flaky_infra":"Infrastructure or test flakiness, not a code defect",
               "real_regression":"A code change broke behaviour that used to work",
               "config_error":"A misconfiguration in the pipeline or environment",
               "cannot_tell":"The information given does not identify a cause"}},
 "severity":{"type":"score","instructions":"How urgently does this failure need a person to act?",
   "criteria":["a retry is a reasonable first response","it needs a fix in the next few days","it blocks the release"]},
 "enough_info":{"type":"noul","instructions":"The information given is sufficient to identify which change caused this failure."},
}
# F3: identical meaning, different numeric notation
run("CI/notation/seconds", {"job":"integration-tests",
  "log":"Step 'integration-tests' timed out after 30 s (limit: 60 s)."}, Q_CI)
run("CI/notation/millis", {"job":"integration-tests",
  "log":"Step 'integration-tests' timed out after 30000 ms (limit: 60000 ms)."}, Q_CI)
run("CI/notation/gigabytes", {"job":"build",
  "log":"OOMKilled: container used 3.8 GB of its 4 GB memory limit."}, Q_CI)
run("CI/notation/bytes", {"job":"build",
  "log":"OOMKilled: container used 4080218931 bytes of its 4294967296 byte memory limit."}, Q_CI)
# F2: ablation
FULL_LOG={"job":"unit-tests","log":(
  "FAIL tests/billing/test_invoice.py::test_prorated_refund\n"
  "  assert refund == 1250\n"
  "  E  assert 0 == 1250\n"
  "  tests/billing/test_invoice.py:88: AssertionError\n"
  "  billing/invoice.py:142 in compute_refund"),
  "changed_files":["billing/invoice.py","billing/schedule.py"],
  "branch":"feat/annual-plans"}
run("CI/ablation/full",    FULL_LOG, Q_CI)
run("CI/ablation/partial", {"job":"unit-tests","log":"FAIL tests/billing/test_invoice.py::test_prorated_refund"}, Q_CI)
run("CI/ablation/minimal", {"job":"unit-tests","log":"CI failed."}, Q_CI)
# Recommended design: the comparison is done in code, the RESULT is written in words
run("CI/words/flaky", FULL_LOG|{"history":
  "This test failed on 2 of the last 10 runs. The 8 passing runs and the 2 failing runs were on the same commit."}, Q_CI)
run("CI/words/regression", FULL_LOG|{"history":
  "This test passed on every run before commit 4f1a2c and has failed on every run since. That commit modified billing/invoice.py."}, Q_CI)

# ---------- Case 2: internal issue triage (Japanese) ----------
Q_ISSUE={
 "team":{"type":"choice","instructions":"この報告はどのチームが対応すべきか。",
   "criteria":{"infra":"サーバ・ネットワーク・基盤の問題","app":"アプリケーションの不具合",
               "account":"権限・アカウント設定の問題","cannot_tell":"報告された内容では判断できない"}},
 "urgency":{"type":"score","instructions":"この報告への対応はどの程度急ぐか。",
   "criteria":["様子を見てよい","今週中に対応する","即時に対応する"]},
 "has_repro":{"type":"noul","instructions":"報告には、報告者以外が同じ現象を再現するのに足りる手順が書かれている。"},
 "enough_info":{"type":"noul","instructions":"この報告の内容だけで、どのチームが対応すべきかを判断できる。"},
}
run("ISSUE/full", {"タイトル":"経費精算画面で申請ボタンが押せない",
  "本文":"経費精算画面で、金額を入力したあと申請ボタンが押せません。\n"
        "手順: 1) 経費精算を開く 2) 交通費を選ぶ 3) 金額に 1200 と入力 4) 申請ボタンを押す\n"
        "期待: 申請が完了する / 実際: ボタンが灰色のまま反応しない\n"
        "環境: Chrome 141 / Windows 11 / 社内ネットワーク\n"
        "影響: 同じ部の3人で再現。今週が精算締切です。"}, Q_ISSUE)
run("ISSUE/partial", {"タイトル":"経費精算画面で申請ボタンが押せない",
  "本文":"経費精算画面で申請ボタンが押せません。困っています。"}, Q_ISSUE)
run("ISSUE/minimal", {"タイトル":"動きません","本文":"動きません。"}, Q_ISSUE)
run("ISSUE/repro_incomplete", {"タイトル":"経費精算画面で申請ボタンが押せない",
  "本文":"経費精算画面で、金額を入力したあと申請ボタンが押せません。\n"
        "手順: 1) 経費精算を開く 2) しばらく操作する\n"
        "環境: 会社のPCです。"}, Q_ISSUE)

# ---------- Case 3: loop control ----------
Q_LOOP={
 "next":{"type":"choice","instructions":"What should the agent do next?",
   "criteria":{"continue":"Attempt another fix on its own",
               "ask_human":"Ask a person for information or a decision before continuing",
               "stop":"Stop and report that the task cannot be completed"}},
 "enough_info":{"type":"noul","instructions":"The recorded attempts contain enough information to choose a next action that is likely to succeed."},
}
run("LOOP/evidence_rich", {"goal":"Make tests/billing/test_invoice.py::test_prorated_refund pass",
  "attempts":[{"n":1,"change":"changed rounding in compute_refund","result":"assert 0 == 1250, same failure"},
              {"n":2,"change":"passed proration_days explicitly","result":"assert 0 == 1250, same failure"},
              {"n":3,"change":"logged inputs","result":"proration_days arrives as 0; the caller in schedule.py never sets it"}]}, Q_LOOP)
run("LOOP/evidence_poor", {"goal":"Make tests/billing/test_invoice.py::test_prorated_refund pass",
  "attempts":[{"n":1,"change":"changed rounding in compute_refund","result":"still failing"}]}, Q_LOOP)
run("LOOP/repeated_same", {"goal":"Make tests/billing/test_invoice.py::test_prorated_refund pass",
  "attempts":[{"n":i,"change":"adjusted rounding in compute_refund","result":"assert 0 == 1250, same failure"}
              for i in range(1,6)]}, Q_LOOP)

# ---------- Case 4: review finding disposition ----------
Q_REVIEW={
 "disposition":{"type":"choice","instructions":"How should this automated review finding be handled?",
   "criteria":{"auto_fix":"Apply the suggested change without a person looking at it",
               "human_review":"A person should decide before anything changes",
               "dismiss":"The finding is not correct or not worth acting on"}},
 "grounded":{"type":"noul","instructions":"The finding is supported by the code shown in the diff."},
}
DIFF=("+def compute_refund(amount, proration_days):\n"
      "+    unused = amount * 0\n"
      "+    return round(amount * proration_days / 30)\n")
run("REVIEW/obvious", {"diff":DIFF,"finding":"`unused` is assigned but never read. Remove it."}, Q_REVIEW)
run("REVIEW/debatable", {"diff":DIFF,"finding":"`compute_refund` should be named `calculate_refund_amount` for consistency with the rest of the module."}, Q_REVIEW)
run("REVIEW/false_positive", {"diff":DIFF,"finding":"`compute_refund` calls `decimal.Decimal` without setting precision, which will lose cents."}, Q_REVIEW)

# ---------- Case 5: log monitoring ----------
Q_MON={
 "action":{"type":"choice","instructions":"What should be done about this log line?",
   "criteria":{"ignore":"No action needed","ticket":"File a ticket for someone to look at during working hours",
               "page":"Wake someone up now"}},
}
LINE="2026-09-22T03:14:07Z ERROR payments.worker: retry 3/3 failed for charge ch_9f21: upstream returned 503"
for i in (1,2,3):
    run(f"MON/repeat#{i}", {"line":LINE}, Q_MON)
run("MON/straddle_low",  {"line":"2026-09-22T03:14:07Z WARN payments.worker: retry 1/3 for charge ch_9f21: upstream returned 503"}, Q_MON)
run("MON/straddle_high", {"line":"2026-09-22T03:14:07Z ERROR payments.worker: all retries failed for 4182 charges in the last 5 minutes: upstream returned 503"}, Q_MON)

json.dump(results, open("jev_results_ops.json","w"), indent=1, ensure_ascii=False)
print("\nwrote jev_results_ops.json")

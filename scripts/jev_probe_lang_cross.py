"""Same issue-triage cells in Japanese and English. Only the language changes."""
import json, os, urllib.request
URL="https://api.typesafe.ai/v1/systemone"; KEY=os.environ["TYPESAFE_API_KEY"]

Q_JA={
 "team":{"type":"choice","instructions":"この報告はどのチームが対応すべきか。",
   "criteria":{"infra":"サーバ・ネットワーク・基盤の問題","app":"アプリケーションの不具合",
               "account":"権限・アカウント設定の問題","cannot_tell":"報告された内容では判断できない"}},
 "urgency":{"type":"score","instructions":"この報告への対応はどの程度急ぐか。",
   "criteria":["様子を見てよい","今週中に対応する","即時に対応する"]},
 "has_repro":{"type":"noul","instructions":"報告には、報告者以外が同じ現象を再現するのに足りる手順が書かれている。"},
 "enough_info":{"type":"noul","instructions":"この報告の内容だけで、どのチームが対応すべきかを判断できる。"}}
Q_EN={
 "team":{"type":"choice","instructions":"Which team should handle this report?",
   "criteria":{"infra":"A server, network or platform problem","app":"An application defect",
               "account":"A permission or account configuration problem",
               "cannot_tell":"The report as given does not identify a team"}},
 "urgency":{"type":"score","instructions":"How urgently does this report need to be handled?",
   "criteria":["Can wait and be observed","Handle within this week","Handle immediately"]},
 "has_repro":{"type":"noul","instructions":"The report contains steps sufficient for someone other than the reporter to reproduce the same behaviour."},
 "enough_info":{"type":"noul","instructions":"The content of this report alone is enough to decide which team should handle it."}}

S_JA={
 "full":{"タイトル":"経費精算画面で申請ボタンが押せない",
  "本文":"経費精算画面で、金額を入力したあと申請ボタンが押せません。\n"
        "手順: 1) 経費精算を開く 2) 交通費を選ぶ 3) 金額に 1200 と入力 4) 申請ボタンを押す\n"
        "期待: 申請が完了する / 実際: ボタンが灰色のまま反応しない\n"
        "環境: Chrome 141 / Windows 11 / 社内ネットワーク\n"
        "影響: 同じ部の3人で再現。今週が精算締切です。"},
 "partial":{"タイトル":"経費精算画面で申請ボタンが押せない",
  "本文":"経費精算画面で申請ボタンが押せません。困っています。"},
 "minimal":{"タイトル":"動きません","本文":"動きません。"},
 "repro_incomplete":{"タイトル":"経費精算画面で申請ボタンが押せない",
  "本文":"経費精算画面で、金額を入力したあと申請ボタンが押せません。\n"
        "手順: 1) 経費精算を開く 2) しばらく操作する\n"
        "環境: 会社のPCです。"}}
S_EN={
 "full":{"title":"Cannot press the submit button on the expense claim screen",
  "body":"On the expense claim screen, after entering the amount, the submit button cannot be pressed.\n"
        "Steps: 1) Open expense claims 2) Select travel expenses 3) Enter 1200 as the amount 4) Press submit\n"
        "Expected: the claim is submitted / Actual: the button stays greyed out and does not respond\n"
        "Environment: Chrome 141 / Windows 11 / internal network\n"
        "Impact: reproduced by 3 people in the same department. The claim deadline is this week."},
 "partial":{"title":"Cannot press the submit button on the expense claim screen",
  "body":"I cannot press the submit button on the expense claim screen. I am stuck."},
 "minimal":{"title":"It does not work","body":"It does not work."},
 "repro_incomplete":{"title":"Cannot press the submit button on the expense claim screen",
  "body":"On the expense claim screen, after entering the amount, the submit button cannot be pressed.\n"
        "Steps: 1) Open expense claims 2) Operate it for a while\n"
        "Environment: a company PC."}}


out={}
def run(name, state, q):
    b=json.dumps({"state":state,"model":"jev-latest","questions":q}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    d=json.load(urllib.request.urlopen(r,timeout=60)); a=d["answers"]
    out[name]={"model":d.get("model"),"team":a["team"]["choice"],
      "team_conf":round(a["team"]["confidence"],3),
      "urgency":round(a["urgency"]["score"],2),"urgency_conf":round(a["urgency"]["confidence"],3),
      "has_repro":round(a["has_repro"]["noul"],3),"enough_info":round(a["enough_info"]["noul"],3)}
    o=out[name]
    print(f"{name:30} {o['team']:12} conf={o['team_conf']:.2f}  urg={o['urgency']:.2f}/{o['urgency_conf']:.2f}  "
          f"repro={o['has_repro']:.2f} enough={o['enough_info']:.2f}",flush=True)

# missing quadrants of the 2x2
for k in S_JA: run(f"stateJA_qEN/{k}", S_JA[k], Q_EN)   # data stays Japanese, prompt in English
for k in S_EN: run(f"stateEN_qJA/{k}", S_EN[k], Q_JA)   # mirror
json.dump(out,open("jev_results_lang_cross.json","w"),indent=1,ensure_ascii=False)

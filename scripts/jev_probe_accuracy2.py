#!/usr/bin/env python3
"""Harder round: the surface wording points at the wrong team. JA vs EN."""
import json, os, time, urllib.request, urllib.error
URL="https://api.typesafe.ai/v1/systemone"; KEY=os.environ["TYPESAFE_API_KEY"]
Q_JA={"team":{"type":"choice","instructions":"この報告はどのチームが対応すべきか。",
   "criteria":{"infra":"サーバ・ネットワーク・基盤の問題","app":"アプリケーションの不具合",
               "account":"権限・アカウント設定の問題","cannot_tell":"報告された内容では判断できない"}}}
Q_EN={"team":{"type":"choice","instructions":"Which team should handle this report?",
   "criteria":{"infra":"A server, network or platform problem","app":"An application defect",
               "account":"A permission or account configuration problem",
               "cannot_tell":"The report as given does not identify a team"}}}

# (正解, 表面が指す先, 日本語, English)
CASES=[
 ("app","infra","申請画面で「サーバーエラーが発生しました」と赤字で表示されます。ただし必ず、郵便番号を半角ハイフンありで入力したときだけ出ます。ハイフンなしで入力すれば同じ操作で成功します。",
  "The application screen shows 'A server error has occurred' in red. However, it only ever appears when the postal code is entered with a hyphen. Entering it without a hyphen succeeds with the same operation."),
 ("infra","app","勤怠画面だけが真っ白で表示されます。ただし東京オフィスからのみで、大阪オフィスと在宅からは正常です。先週このビルの回線工事がありました。",
  "The attendance screen renders completely blank. This happens only from the Tokyo office; from the Osaka office and from home it is fine. There was line work in this building last week."),
 ("account","app","保存ボタンを押すと「エラーが発生しました」とだけ出て保存できません。同じ画面で同じ操作を、先月入った契約社員だけができず、正社員は全員できます。",
  "Pressing save shows only 'An error has occurred' and does not save. On the same screen with the same operation, only the contract staff who joined last month cannot do it; all permanent staff can."),
 ("app","account","経費精算の承認画面で「権限がありません」と表示されます。システム管理者のアカウントでも同じ表示が出ます。先週のリリース以降、全員がこの状態です。",
  "The expense approval screen shows 'You do not have permission'. The same message appears even on the system administrator account. Everyone has been in this state since last week's release."),
 ("infra","account","社内の全員がログインできません。IDもパスワードも変えていません。認証サーバに ping が通らないと情報システム部から連絡がありました。",
  "Nobody in the company can log in. No IDs or passwords have changed. IT has reported that the authentication server does not respond to ping."),
 ("app","infra","月次レポート画面だけが必ずタイムアウトします。他の画面は速いままです。対象月を1か月にすると出ますが、12か月にすると必ず落ちます。",
  "Only the monthly report screen always times out. Other screens remain fast. It renders when the target period is one month, but always fails when set to twelve months."),
 ("account","infra","新設された品質保証部のメンバーだけ、共有フォルダが一覧に出てきません。同じPC・同じネットワークで、他部署の人がログインすると見えます。",
  "Only members of the newly created QA department do not see the shared folder in the list. On the same PC and the same network, people from other departments see it when they log in."),
 ("infra","app","商品画像が途中で切れて表示されます。社内Wi-Fi経由のときだけで、携帯回線だと正常です。画像ファイル自体は開けば壊れていません。",
  "Product images render truncated. This happens only over the office Wi-Fi; over a mobile connection they are fine. The image files themselves are not corrupted when opened directly."),
]
out={}
def ask(st,q):
    b=json.dumps({"state":st,"model":"jev-latest","questions":q}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    for attempt in range(6):
        try:
            return json.load(urllib.request.urlopen(r,timeout=90))
        except urllib.error.HTTPError as e:
            if e.code in (429,500,502,503,520,524) and attempt<5:
                time.sleep(2**attempt); continue
            raise
for lang,q,idx in (("JA",Q_JA,2),("EN",Q_EN,3)):
    for i,c in enumerate(CASES):
        d=ask({"本文" if lang=="JA" else "body": c[idx]},q); a=d["answers"]["team"]
        k=f"{lang}/{i:02d}"
        out[k]={"gold":c[0],"lure":c[1],"choice":a["choice"],"confidence":round(a["confidence"],3),
                "probabilities":{x:round(y,2) for x,y in a["probabilities"].items()},"model":d.get("model")}
        mark="OK " if a["choice"]==c[0] else ("LURE" if a["choice"]==c[1] else ("--  " if a["choice"]=="cannot_tell" else "NG "))
        print(f"{mark:5}{k} gold={c[0]:8} lure={c[1]:8} got={a['choice']:12} conf={a['confidence']:.2f}",flush=True)
json.dump(out,open("jev_results_accuracy2.json","w"),indent=1,ensure_ascii=False)

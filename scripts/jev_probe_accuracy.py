#!/usr/bin/env python3
"""Accuracy against ground-truth labels, Japanese vs English. Same 12 issues in both."""
import json, os, urllib.request
URL="https://api.typesafe.ai/v1/systemone"; KEY=os.environ["TYPESAFE_API_KEY"]

Q_JA={"team":{"type":"choice","instructions":"この報告はどのチームが対応すべきか。",
   "criteria":{"infra":"サーバ・ネットワーク・基盤の問題","app":"アプリケーションの不具合",
               "account":"権限・アカウント設定の問題","cannot_tell":"報告された内容では判断できない"}}}
Q_EN={"team":{"type":"choice","instructions":"Which team should handle this report?",
   "criteria":{"infra":"A server, network or platform problem","app":"An application defect",
               "account":"A permission or account configuration problem",
               "cannot_tell":"The report as given does not identify a team"}}}

# (label, 日本語本文, English body)
CASES=[
 ("infra","社外のネットワークからは社内ポータルが開きますが、社内のオフィスLANからだと接続がタイムアウトします。同じPCで場所を変えるだけで再現します。",
   "The internal portal opens from an outside network, but from the office LAN the connection times out. It reproduces on the same PC just by changing location."),
 ("account","管理メニューが自分のアカウントにだけ表示されません。同じ部署の同僚のアカウントでは同じ画面に表示されています。",
   "The admin menu does not appear for my account only. On a colleague's account in the same department it appears on the same screen."),
 ("app","請求書の合計金額が明細の合計と1円ずれます。明細が3件以上で、単価に小数が含まれるときだけ起きます。",
   "The invoice total differs from the sum of the line items by one yen. It only happens when there are three or more line items and the unit prices contain decimals."),
 ("infra","毎朝9時ちょうどから15分ほど、全社のどの画面も表示に10秒以上かかります。9時20分を過ぎると元に戻ります。",
   "Every morning from exactly 9:00 for about 15 minutes, every screen company-wide takes more than 10 seconds to load. After 9:20 it returns to normal."),
 ("account","先月退職した社員のIDで、いまもログインできる状態になっています。人事システムでは退職済みになっています。",
   "An employee who left last month can still log in with their ID. The HR system already shows them as having left."),
 ("app","会社名の検索で「株式会社」を含む名前がヒットしません。「株式会社」を除いて入力すると見つかります。",
   "Searching for company names containing the Japanese word for 'corporation' returns no hits. Removing that word from the query finds them."),
 ("infra","5MBを超えるファイルを添付すると必ず 502 Bad Gateway が返ります。5MB以下なら成功します。",
   "Attaching a file larger than 5MB always returns 502 Bad Gateway. Files of 5MB or less succeed."),
 ("account","先月に営業部から総務部へ異動しましたが、いまも営業部あての承認依頼が自分に届きます。総務部あての依頼は届きません。",
   "I transferred from Sales to General Affairs last month, but approval requests addressed to Sales still come to me. Requests addressed to General Affairs do not."),
 ("app","一覧の日付欄が 2026/13/01 と表示されます。詳細画面では 2026/01/13 と正しく出ます。",
   "The date column in the list shows 2026/13/01. On the detail screen it correctly shows 2026/01/13."),
 ("infra","VPNに接続している間だけ、画面内の画像がすべて読み込まれません。VPNを切ると表示されます。",
   "While connected to the VPN, none of the images on the screen load. They display once the VPN is disconnected."),
 ("account","今月入社した新人がログインできません。IDとパスワードは発行済みで、本人は正しく入力しています。",
   "A new hire who joined this month cannot log in. Their ID and password have been issued and they are entering them correctly."),
 ("app","入力途中で戻るボタンを押すと、それまで入力した内容がすべて消えます。ブラウザの戻るでも同じです。",
   "Pressing the back button partway through input clears everything entered so far. The browser's back button does the same."),
]

out={}
def ask(state,q):
    b=json.dumps({"state":state,"model":"jev-latest","questions":q}).encode()
    r=urllib.request.Request(URL,data=b,headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))

for lang,q,idx in (("JA",Q_JA,1),("EN",Q_EN,2)):
    for i,c in enumerate(CASES):
        d=ask({"本文" if lang=="JA" else "body": c[idx]}, q)
        a=d["answers"]["team"]
        k=f"{lang}/{i:02d}"
        out[k]={"gold":c[0],"choice":a["choice"],"confidence":round(a["confidence"],3),
                "probabilities":{x:round(y,2) for x,y in a["probabilities"].items()},"model":d.get("model")}
        ok="OK " if a["choice"]==c[0] else ("-  " if a["choice"]=="cannot_tell" else "NG ")
        print(f"{ok}{k}  gold={c[0]:8} got={a['choice']:12} conf={a['confidence']:.2f}",flush=True)
json.dump(out,open("jev_results_accuracy.json","w"),indent=1,ensure_ascii=False)

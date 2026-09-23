# jev-confidence-experiments

Zenn の記事「[Jevが返すconfidenceの意味〜Jevの応答を受けてループエンジニアリングでどう捌くか〜](https://zenn.dev/uehaj/articles/jev-confidence-dispatch)」で使った実測のスクリプトと結果です。記事の各表の数値は、ここにある JSON から取っています。

## 前提

- 対象は TypeSafe の System One API（`jev-latest`）です。測定は 2026年9月22日〜23日に行いました。
- **入力はすべて、生成 AI にダミーデータとして作らせたものです。** CI ログ、社内イシュー、レビュー指摘、ログ行、試行履歴のいずれも実運用のデータではありません。
- 各セルは質問文を一通りしか試していません。質問文を書き換えれば値は動きます。

## 構成

```
scripts/   測定スクリプト（jev_probe_*.py）
results/   保存した結果（jev_results_*.json）
```

結果は計 147 件です。通信エラーで再試行したリクエストは数えていません。

## 記事の箇所との対応

| 記事の箇所 | ファイル（results/） | キー |
|---|---|---|
| confidence は分布の尖り具合（確率と confidence の表） | `jev_results_conf.json` | `G/*` の `level` |
| 高い confidence が意味しないこと（`cannot_tell` の有無の対照） | `jev_results_cannottell.json` | `PAY/minimal/*`、`CI/minimal/*` |
| 低い confidence が意味しないこと | `jev_results_contra.json`、`jev_results_split.json` | `C1/history_B_only`、`A/monitor/cannot_tell#1` |
| ケース1　ログの量を変えた表 | `jev_results_ops.json` | `CI/ablation/full`、`CI/ablation/partial`、`CI/ablation/minimal` |
| ケース1　履歴の渡し方の表（ログのみ 0.20／文章 0.41／配列 0.68） | `jev_results_ops.json`、`jev_results_contra.json` | `CI/ablation/full`、`C2/history_as_words`、`C2/history_as_numbers`（`enough_info`） |
| ケース1　候補の拮抗（0.51 対 0.48、confidence 0.35） | `jev_results_contra.json` | `C1/history_B_only` |
| ケース1　コラム「証拠が矛盾していれば割れる、ではありませんでした」 | `jev_results_contra.json` | `C1/history_A_only`、`C1/contradiction_A_and_B` |
| 測っていないこと（`30 s` と `30000 ms`、緊急度の confidence 0.84 と 0.75） | `jev_results_ops.json` | `CI/notation/seconds`、`CI/notation/millis` の `severity[1]` |
| ケース2　社内イシューのトリアージ | `jev_results_ops.json` | `ISSUE/*` |
| コラム「質問や指示は英語にすべきか」 | `jev_results_lang.json`、`jev_results_lang_cross.json`、`jev_results_accuracy.json`、`jev_results_accuracy2.json` | すべて |
| ケース3　ループを続けるか人を呼ぶか | `jev_results_ops.json` | `LOOP/*` |
| ケース4　レビュー指摘の採否 | `jev_results_ops.json`、`jev_results_split.json` | `REVIEW/*`、`A/review/cannot_tell` |
| ケース5　ログ行の扱いを決める | `jev_results_ops.json`、`jev_results_split.json` | `MON/*`、`A/monitor/*` |
| cannot_tell は常に入れるべきか | `jev_results_cost.json` | すべて |
| Choice、Score、Noul それぞれの confidence 値（段階数・4択） | `jev_results_score.json`、`jev_results_split.json` | すべて、`B/*` |
| 測っていないこと（架空の通貨で桁だけ変えた Noul 0.61 → 0.28） | `jev_results_c5.json` | `C5/house12`、`C5/house120000` の `unfair` |
| 補集合ではない二命題の回答例（0.07 と 0.05） | `jev_results.json` | `F/salary/$5,000,000` |

`jev_results.json` の `A/*`〜`E/*`、`jev_results_c2.json`〜`jev_results_c4.json`、`jev_results_ops.json` の `CI/words/*` は、記事の初期の版で使った系列です（架空の通貨での桁の効果の検討と、同一入力の繰り返し、日英比較）。

同じ入力を別の系列で測り直したものは、値がわずかに異なることがあります。たとえば未使用変数の指摘は `jev_results_ops.json` の `REVIEW/obvious` で 0.93、`jev_results_cost.json` の `review_obvious/3択(既測)` で 0.92 です。

## 注意点

- **モデルのバージョン**: レスポンスの `model` を保存しているのは `jev_results_contra.json`、`jev_results_lang.json`、`jev_results_lang_cross.json`、`jev_results_accuracy.json`、`jev_results_accuracy2.json` で、いずれも `jev-1.13.0` です。それ以外の系列は `model` を保存していません。
- **保存時の加工**: 結果の JSON は API の生のレスポンスではありません。各スクリプトが、必要な項目の抜き出しと小数の丸めをして保存しています。とくに `jev_results_conf.json` は、確率をカテゴリ名なしの配列で保存しており、配列の並びもカテゴリの順と対応していません。この系列からは、最大の確率とその値は読めますが、どのカテゴリに何割付いたかは復元できません。
- **公開にあたって除いた列**: `jev_results_conf.json` と `jev_probe_conf.py` から、公式が開示していない計算式を当てはめた比較列（`entropy_formula`）を除いています。公開準備で手を加えたのはこの列だけです。
- **無効な比較**: `jev_results_ops.json` の `CI/notation/gigabytes` と `CI/notation/bytes` は、`3.8 GB` と `4080218931 bytes`（十進で約 4.08 GB）を比べていて、量が一致していません。記事ではこの組を結果から除いています。
- **`cannot_tell` の説明文**: `jev_results_split.json` の `A/monitor/*` と `A/review/cannot_tell`、`jev_results_cost.json` の `review_obvious/4択(+ct)` では、`cannot_tell` の説明文に足りない情報を具体的に書いています。汎用的な「判断できない」との比較ではありません。

## 実行

```bash
export TYPESAFE_API_KEY=...   # 自分の API キー
python3 scripts/jev_probe_ops.py
```

スクリプトは結果の JSON をカレントディレクトリに書き出します。API は課金されるので、実行前に各スクリプトのリクエスト数を確認してください。

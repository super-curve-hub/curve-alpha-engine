# Curve Alpha Engine v2 Complete

マクロ対応型マルチファクター株式ランキングエンジン。

## 統合ファクター

- Quality
- Value
- Momentum
- Risk
- Macro
- Flow
- Theme

## 起動方法

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 月次ランキング生成

```bash
python run_monthly.py
```

## 出力

```text
output/curve_alpha_ranking.csv
output/monthly_top20.md
```

## 注意

- `yfinance` で取得できない銘柄は、一部項目が欠損します。
- SPCXのような特殊銘柄・未上場/新規上場銘柄は、`universe_default.csv` と手入力CSVで補完してください。

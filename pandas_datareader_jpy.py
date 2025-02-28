import csv
from pathlib import Path
import pandas as pd
import yfinance as yf

# 複数の銘柄を指定
tickers = []
base_path = Path(__file__).parent
path_dif = base_path / 'csv_reserch.csv'
# path_dif = base_path / 'csv_reserch_new.csv'

with path_dif.open(mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        key = row['銘柄コード'] + '.T'
        tickers.append(key)

print(tickers)

# 結果を格納するデータフレームを初期化
result_df = pd.DataFrame()

# 各銘柄に対してデータを取得し、データフレームに追加
for ticker in tickers:
    # auto_adjust=False を設定して、'Adj Close'列を取得する
    df = yf.download(ticker, start="2025-01-01", end="2026-01-01", auto_adjust=False)

    # データフレームの列を確認（デバッグ用）
    print(f"Columns for {ticker}: {df.columns.tolist()}")

    # 'Close'列を前日の終値にずらす
    df['Previous_Close'] = df['Close'].shift(1)

    # 'Adj Close'列が存在するか確認
    if 'Adj Close' in df.columns:
        # 最終行の'Adj Close'列のデータを取得（数値のみ）
        last_row_adj_close = float(df['Adj Close'].iloc[-1])
    else:
        # 'Adj Close'がない場合は'Close'を使用（数値のみ）
        last_row_adj_close = float(df['Close'].iloc[-1])
        print(f"Warning: 'Adj Close' column not found for {ticker}, using 'Close' instead.")

    # データをデータフレームに追加
    result_df = pd.concat([result_df, pd.DataFrame({'Ticker': ticker[:4], 'Last_Row_Adj_Close': [last_row_adj_close]})])

# 結果をCSVファイルに保存
result_df.to_csv("result_data.csv", index=False)

# 結果の表示
print(result_df)
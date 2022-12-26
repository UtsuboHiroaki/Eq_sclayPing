import csv
import json
import os
import pprint
import re
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta

"""
ZIPファイルのダウンロード専用
"""
edinet_url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents.json"
codes = []
year = 0
month = 19
day = 0
annual = True
quarter = False

#差分リストから銘柄コ－ドを取り出す

base_path = Path(__file__).parent
path_dif = base_path / 'screening' / 'csv_differ.csv'
with path_dif.open(mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        key = row['銘柄コード']
        codes.append(key)

print(codes)

# codesを文字型の配列に統一する．
if codes != None:
    if type(codes) in (str, int, float):
        codes = [int(codes)]

# datetime型でfor文を回す
def date_range(start, stop, step=timedelta(1)):
    current = start
    while current < stop:
        yield current
        current += step


# 結果を格納するDataFrameを用意
database = pd.DataFrame(index=[], columns=['code', 'type', 'date', 'title', 'URL'])

for d in date_range(date.today() - relativedelta(years=year, months=month, days=day) + relativedelta(days=1),
                    date.today() + relativedelta(months=-17)):
    # EDINET API にアクセス
    d_str = d.strftime('%Y-%m-%d')
    params = {'date': d_str, 'type': 2}
    res = requests.get(edinet_url, params=params, verify=False)
    json_res = json.loads(res.text)
    time.sleep(5)

    # 正常にアクセスできない場合
    if json_res['metadata']['status'] != '200':
        print(d_str, 'not accessible')
        continue

    print(d_str, json_res['metadata']['resultset']['count'])  # 日付と件数を表示

    # 0件の場合
    if len(json_res['results']) == 0:
        continue

    df = pd.DataFrame(json_res['results'])[['docID', 'secCode', 'ordinanceCode', 'formCode', 'docDescription']]
    df.dropna(subset=['docID'], inplace=True)
    df.dropna(subset=['secCode'], inplace=True)
    df.rename(columns={'secCode': 'code', 'docDescription': 'title'}, inplace=True)
    df['date'] = d
    df['URL'] = df['docID']
    df['URL'] = "https://disclosure.edinet-fsa.go.jp/api/v1/documents/" + df['URL']

    for code in codes:
        # 4桁の証券コードを5桁に変換
        if len(str(int(code))) == 4:
            code = str(int(code)) + '0'
        # 指定された証券コードのみを抽出
        if code != None:
            df0 = df[df['code'] == code]
            if not df0.empty:
                if annual == True:
                    df1 = df0[(df0['ordinanceCode'] == '010') & (df0['formCode'] == '030000')]
                    df1['type'] = 'annual'
                    #if database.empty:
                    database = pd.concat([database, df1[['code', 'type', 'date', 'title', 'URL']]], axis=0,
                                             join='outer').reset_index(drop=True)
                if quarter == True:
                    df2 = df0[(df0['ordinanceCode'] == '010') & (df0['formCode'] == '043000')]
                    df2['type'] = 'quarter'
                    if database.empty:
                        database = pd.concat([database, df2[['code', 'type', 'date', 'title', 'URL']]], axis=0,
                                             join='outer').reset_index(drop=True)
pprint.pprint(database)
#csvでリンク先デ－タ排出
path_edi_Url = base_path / 'CASAFLOWDATA' / 'csv_edinet_url.csv'
database.to_csv(path_edi_Url, encoding='utf-8', index=True)
#    return database
codes2 = []
keys = database['code']
for key in keys:
    key_code = key[:4]
    if key_code in codes:
        codes2.append(str(key_code))

codes = codes2
if codes == None:
    codes = [None]
else:
    if type(codes) in (str, int, float):
        codes = [int(codes)]
    for i, code in enumerate(codes):
        if len(str(int(code))) == 4:
            codes[i] = str(int(code)) + '0'
        if code == None:
            df_company = database
        else:
            df_company = database[database['code'] == codes[i]]
            df_company = df_company.reset_index(drop=True)

            # 証券コードをディレクトリ名とする
            dir_path = database.loc[i, 'code']
            if os.path.exists(dir_path) == False:
                os.mkdir(dir_path)

            for i in range(df_company.shape[0]):
                if (df_company.loc[i, 'type'] == 'annual') or (df_company.loc[i, 'type'] == 'quarter'):
                    params = {"type": 1}
                    res = requests.get(df_company.loc[i, 'URL'], params=params, stream=True)
                    if df_company.loc[i, 'type'] == 'annual':
                        # 有価証券報告書のファイル名は"yyyy_0.zip"
                        filename = dir_path + r'/' + str(df_company.loc[i, 'date'].year) + r"_0.zip"
                    elif df_company.loc[i, 'type'] == 'quarter':
                        if re.search('期第', df_company.loc[i, 'title']) == None:
                            # 第何期か不明の四半期報告書のファイル名は"yyyy_unknown_docID.zip"
                            filename = dir_path + r'/' + str(df_company.loc[i, 'date'].year) + r'_unknown_' + \
                                       df_company.loc[
                                           i, 'URL'][
                                       -8:] + r'.zip'
                        else:
                            # 四半期報告書のファイル名は"yyyy_quarter.zip"
                            filename = dir_path + r'/' + str(df_company.loc[i, 'date'].year) + r'_' + \
                                       df_company.loc[i, 'title'][
                                           re.search('期第', df_company.loc[i, 'title']).end()] + r'.zip'
                # 同名のzipファイルが存在する場合，上書きはしない
                if os.path.exists(filename):
                    print(df_company.loc[i, 'code'], df_company.loc[i, 'date'], 'already exists')
                    continue

                # 正常にアクセスできた場合のみzipファイルをダウンロード
                if res.status_code == 200:
                    with open(filename, 'wb') as file:
                        for chunk in res.iter_content(chunk_size=1024):
                            file.write(chunk)
                        print(df_company.loc[i, 'code'], df_company.loc[i, 'date'], 'saved')
                        sec_code = df_company.loc[i, 'code']
                        dow_data = df_company.loc[i, 'title']
    print('done!')

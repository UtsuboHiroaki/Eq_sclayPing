import csv
import json
import pprint
import re
import time
from datetime import date, timedelta
from pathlib import Path

import requests
from dateutil.relativedelta import relativedelta


def csv_open(csv_file_path):
    """
    csvファイルの読み込み
    """
    with csv_file_path.open(mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = row['銘柄コード']
            codes.append(key)

# datetime型でfor文を回す
def date_range(start, stop, step=timedelta(1)):
    current = start
    while current < stop:
        yield current
        current += step

def code_fifth(code):
    """
    codeが4桁の時に5桁にする関数
    """
    if len(str(int(code))) == 4:
        code = str(int(code)) + '0'
        return code


# ZIPファイルのダウンロード専用(2023/01/05 書き直し用にRetryのブランチを作成)

edinet_url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents.json"
codes = []
year = 0
month = 7
day = 0
annual = True
quarter = False

# 差分リストから銘柄コ－ドを取り出す

base_path = Path(__file__).parent
path_dif = base_path / 'screening' / 'csv_differ.csv'
csv_open(path_dif)
print(codes)

# codesを文字型の配列に統一する．
if codes is not None:
    if type(codes) in (str, int, float):
        codes = [int(codes)]




# 結果を格納するDataFrameを用意
# database = pd.DataFrame(index=[], columns=['code', 'type', 'date', 'title', 'URL'])
database = []
for d in date_range(date.today() - relativedelta(years=year, months=month, days=day) + relativedelta(days=1),
                    date.today() + relativedelta(months=-6)):
                    # date.today() + relativedelta(days=1)):
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
    for data in json_res['results']:
        if data['secCode'] is None:
            continue
        for code in codes:
            # 4桁の証券コードを5桁に変換
            if len(str(int(code))) == 4:
                code = code_fifth(code)
                if data['secCode'] in code:
                    # データベースに追加
                    if annual:
                        if data['ordinanceCode'] == '010' and data['formCode'] == '030000':
                            database.append({'code': data['secCode'],
                                                        'type': 'annual',
                                                        'date': d,
                                                        'title': data['docDescription'],
                                                        'URL': "https://disclosure.edinet-fsa.go.jp/api/v1/documents/" + data['docID']})
                    if quarter:
                        if data['ordinanceCode'] == '010' and data['formCode'] == '043000':
                            database.append({'code': data['secCode'],
                                                        'type': 'quarter',
                                                        'date': d,
                                                        'title': data['docDescription'],
                                                        'URL': "https://disclosure.edinet-fsa.go.jp/api/v1/documents/" + data['docID']})
    """
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
            code = code_fifth(code)
        # 指定された証券コードのみを抽出
        if code is not None:
            df0 = df[df['code'] == code]
            if not df0.empty:
                if annual:
                    df1 = df0[(df0['ordinanceCode'] == '010') & (df0['formCode'] == '030000')]
                    df1['type'] = 'annual'
                    database = pd.concat([database, df1[['code', 'type', 'date', 'title', 'URL']]], axis=0,
                                             join='outer').reset_index(drop=True)
                if quarter:
                    df2 = df0[(df0['ordinanceCode'] == '010') & (df0['formCode'] == '043000')]
                    df2['type'] = 'quarter'
                    if database.empty:
                        database = pd.concat([database, df2[['code', 'type', 'date', 'title', 'URL']]], axis=0,
                                             join='outer').reset_index(drop=True)
    """
pprint.pprint(database)
#csvでリンク先デ－タ排出
# path_edi_Url = base_path / 'CASAFLOWDATA' / 'csv_edinet_url.csv'
# database.to_csv(path_edi_Url, encoding='utf-8', index=True)
#    return database
# codes2 = []
# keys = database['code']
# for key in keys:
#     key_code = key[:4]
#     if key_code in codes:
#         codes2.append(str(key_code))

# codes = codes2
# if codes is None:
#     codes = [None]
# else:
#     if type(codes) in (str, int, float):
#         codes = [int(codes)]
    # for i, code in enumerate(codes):
#     for code in codes:
        # if code is None:
        #     df_company = database
        # else:
          #  df_company = database[database['code'] == codes[i]]
          #  df_company = df_company.reset_index(drop=True)
for data in database:
    # 証券コードをディレクトリ名とする
    code = data['code']
    if len(str(int(code))) == 4:
        code = str(int(code)) + '0'
    dir_path = Path.joinpath(base_path, code)
    if dir_path.exists() is False:
        dir_path.mkdir()

    # for i in range(df_company.shape[0]):
    if (data['type'] == 'annual') or (data['type'] == 'quarter'):
        params = {"type": 1}
        res = requests.get(data['URL'], params=params, stream=True)
        if data['type'] == 'annual':
            # 有価証券報告書のファイル名は"yyyy_0.zip"
            filename = Path.joinpath(dir_path, str(data['date'].year) + '_0.zip')
            # filename = dir_path + r'/' + str(data['date'].year) + r"_0.zip"
        elif data['type'] == 'quarter':
            if re.search('期第', data['title']) == None:
                # 第何期か不明の四半期報告書のファイル名は"yyyy_unknown_docID.zip"
                filename = dir_path + r'/' + str(data['date'].year) + r'_unknown_' + \
                           data['URL'][-8:] + r'.zip'
            else:
                # 四半期報告書のファイル名は"yyyy_quarter.zip"
                filename = dir_path + r'/' + str(data['date'].year) + r'_' + \
                           data['title'][
                               re.search('期第', data['title']).end()] + r'.zip'
        # 同名のzipファイルが存在する場合，上書きはしない
    if filename.exists() is True:
        print(data['code'], data['date'], 'already exists')
        continue

    # 正常にアクセスできた場合のみzipファイルをダウンロード
    if res.status_code == 200:
        with open(filename, 'wb') as file:
            for chunk in res.iter_content(chunk_size=1024):
                file.write(chunk)
            print(data['code'], data['date'], 'saved')
            sec_code = data['code']
            dow_data = data['title']

print('done!')

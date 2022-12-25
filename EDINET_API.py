import pprint
import time
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import requests
import json
import pandas as pd
import numpy as np
import os
import re
import zipfile
from pathlib import Path
import glob
import shutil
import glob
from bs4 import BeautifulSoup
import csv

"""
このファイルは2巡目以降の作業に使用。一度目はダウンロ－ドまでで終わってよい
"""
# ダウンロ－ドされたHTMLを順に調べる関数。find_word1は調べる財務諸表。word3はその項目
def rearch_data (files, find_word1, find_word3, sec_code, dow_data):
    for target_file in files:
        #print(target_file)
        with open(target_file, encoding='utf-8') as f:
            html = f.read()

        # htmデータの取得
        soup = BeautifulSoup(html, 'html.parser')
        #ヘッダーの文字の大きさが定まらない為可変にする
        for i in range(6):
            hs = "h" + str(i)
            h5s = soup.find_all(hs)
            if h5s:
                for h5 in h5s:
                    h5_word = h5.get_text()
                    # HTMLから連結キャッシュフロー計算書計算書の文字を探し、単位を求める
                    if h5_word.find(find_word1) > 0:
                        tani_moto = h5.find_parent(name='div')
                        data_moto = h5.find_next_siblings(name='div')
                        tag_word2 = 'tr'
                        tag_word3 = 'p'
                        tag_word4 = 'td'
                        find_word2 = '単位：'
                        for tani_gp in tani_moto:
                            if tani_gp.find(tag_word2) != -1 and tani_gp.find(tag_word2) != None:
                                tanis = tani_gp.find(name='tr', text=False)
                                for tani in tanis:
                                    if tani.find(tag_word3) != -1:
                                        tanis_words = tani.find(name='p', text=False)
                                        tani_word = tani.get_text(strip=True)
                                        if tani_word.find(find_word2) > 0:
                                            cash_flow_tani = tani_word
                                            break
                        data_list = []
                        count = 0
                        for data_gp in data_moto:
                            #pprint.pprint(data_gp)
                            if data_gp.find(tag_word2) != -1 and data_gp.find(tag_word2) != None:
                                datas = data_gp.find_all(name='tr', text=False)
                                #pprint.pprint(datas)
                                for data in datas:
                                    #pprint.pprint(data)
                                    data_data_words = data.get_text(strip=True, separator=':')
                                    data_data_words_spl = data_data_words.split(':')
                                    for data_word in data_data_words_spl:
                                        if data_word.find(find_word3) >= 0:
                                            if len(data_data_words_spl) >= 3:
                                                if len(data_data_words_spl) != 3:
                                                    data_data_words_spl = [i for i in data_data_words_spl if i != '△']
                                                data_list.append(data_data_words_spl)
                                                if 'cash_flow_tani' in locals():
                                                    data_list.append(cash_flow_tani)
                                                else:
                                                    data_list.append('単位不明')
                                                data_dict = {
                                                    '銘柄コード': sec_code,
                                                    'デ－タ': dow_data,
                                                    '項目G': data_list[0],
                                                    '単位': data_list[1],
                                                }
                                                cash_flow_list.append(data_dict)
                                                data_list = []
    return cash_flow_list

def create_csv(title, cash_flow_list_kakou):
    """
    csvファイルの生成
    """
    path = Path(__file__).absolute().parent

    today = date.today()
    csv_path = path  / 'CASAFLOWDATA' /  f"{title}{today}.csv"

    # csv.Dictwiter 2行目以降はwriterowsメソッドでrowオブジェクトのイテラブルの全ての要素を指定する
    with csv_path.open(mode="w", encoding="utf-8_sig", newline="") as f:
        field_names = (
            "銘柄コード", "デ－タ", "単位", "項目", "前年", "当年"
        )
        writer = csv.DictWriter(f, fieldnames=field_names, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(cash_flow_list_kakou)

edinet_url = "https://disclosure.edinet-fsa.go.jp/api/v1/documents.json"
#codes = [3738, 4659]
codes = []
year = 1
month = 0
day = 0
annual = True
quarter = False

cash_flow_list = []
find_word1 = '連結キャッシュ・フロー計算書'
find_words = ['営業活動によるキャッシュ・フロー', '減価償却費', '有形固定資産', '無形固定資産']

#差分リストから銘柄コ－ドを取り出す(新しくしたcsv_differ.csvで実施)

base_path = Path(__file__).parent
path_dif = base_path / 'screening' / 'csv_differ.csv'
#初回なので全銘柄(2022/10/10)
#path_dif = base_path / 'screening' / 'csv_reserch.csv'
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
#three_month_ago = date.today() - relativedelta(months=3)
"""
for d in date_range(three_month_ago - relativedelta(years=year, months=month, days=day) + relativedelta(days=1),
                    three_month_ago + relativedelta(days=1)):
"""
for d in date_range(date.today() - relativedelta(years=year, months=month, days=day) + relativedelta(days=1),
                    date.today() + relativedelta(days=1)):
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
                bath_path = Path(__file__).resolve().parent
                target = '/'
                idx = filename.find(target)
                folder = filename[:idx]
                name = filename[idx + 1:]
                filename_zip = os.path.join(bath_path, folder, name)
                with zipfile.ZipFile(filename_zip) as existing_zip:
                    existing_zip.extractall()
                filepath = str(os.path.join(bath_path, 'XBRL', 'PublicDoc'))
                files = glob.glob(filepath + '/*.htm')  # htmファイルの取得
                files = sorted(files)  # ファイルを並び替えているだけ
                for find_word3 in find_words:
                    rearch_data(files, find_word1, find_word3, sec_code, dow_data)
                fold_path = os.path.join(bath_path, 'XBRL')
                shutil.rmtree(fold_path)

    pprint.pprint(cash_flow_list)
    cash_flow_list_kakou = []
    for cash_flow in cash_flow_list:
        detail = cash_flow['項目G']
        cash_flow_dict = {
            '銘柄コード': cash_flow['銘柄コード'],
            'デ－タ' : cash_flow['デ－タ'],
            '単位' : cash_flow['単位'],
            '項目' : detail[0],
            '前年': detail[1],
            '本年': detail[2],
        }
        cash_flow_list_kakou.append(cash_flow_dict)
    title = 'CASAFLOWDATA_'
    create_csv(title, cash_flow_list_kakou)

    print('done!')

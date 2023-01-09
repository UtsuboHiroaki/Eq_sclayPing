from bs4 import BeautifulSoup

from Split.Read_HTML_V10 import find_words2, cash_flow_list


def rearch_data(files, find_word1, sec_code, dow_data, *find_words):
    """
    作業回数を1回にしたいのでカウンタ－設定。counterが1以上ならル－プ抜ける
    ダウンロ－ドされたHTMLを順に調べる関数。find_word1は調べる財務諸表。word3はその項目
    """
    counter = 0
    for target_file in files:
        print(target_file)
        if counter > 0:
            break
        with open(target_file, encoding='utf-8') as f:
            html = f.read()

        # htmデータの取得
        soup = BeautifulSoup(html, 'html.parser')
        # ヘッダーの文字の大きさが定まらない為可変にする
        for i in range(6):
            if counter > 0:
                break
            hs = "h" + str(i)
            h5s = soup.select(hs)
            if h5s:
                for h5 in h5s:
                    if counter > 0:
                        break
                    h5_word = h5.get_text()
                    # HTMLから連結キャッシュフロー計算書計算書の文字を探し、単位を求める
                    if h5_word.find(find_word1) > 0:
                        tani_moto = soup.select('tr p')
                        data_moto = soup.select('tr')
                        data_get(tani_moto, data_moto, find_words, find_words2, sec_code, dow_data)

    return cash_flow_list


def data_get(tani_moto,data_moto, find_words, find_words2, sec_code, dow_data):
    """
    データを取得する関数
    """
    find_word2 = '円'
    for tani_gp in tani_moto:
        tani_words = tani_gp.get_text()
        if tani_words:
            if tani_words.find(find_word2) > 0:
                cash_flow_tani = tani_words
                break
    for find_word3 in find_words:
        if find_word3 in ('営業活動によるキャッシュ・フロー', '減価償却費'):
            word_counter = 1
        else:
            word_counter = 0
        data_list = []
        count = 0
        for data_gp in data_moto:
            if count > 0:
                data_list = []
                count = 0
            if word_counter > 1:
                break
            datas = data_gp.select('p')
            for data in datas:
                data_word = data.get_text()
                data_word_ex = data_word.replace("\n", "")
                if len(data_word_ex.split()) > 0:
                    if data_word_ex.find(find_word3) >= 0 or count > 0:
                        data_list.append(data_word_ex)
                        count += 1
                    if count == 3:
                        if word_counter == 0:
                            find_words2_counter = 0
                            for find_words_2 in find_words2:
                                if data_list[0].find(find_words_2) > 0:
                                    find_words2_counter += 1
                            if find_words2_counter == 0:
                                data_list = []
                                count = 0
                                break
                        data_list.append(cash_flow_tani)
                        data_dict = {
                            '銘柄コード': sec_code,
                            'デ－タ': dow_data,
                            '項目': data_list[0],
                            '前年': data_list[1],
                            '当年': data_list[2],
                            '単位': data_list[3],
                        }
                        cash_flow_list.append(data_dict)
                        data_list = []
                        counter = 1
                        if word_counter > 0:
                            word_counter += 1
                        if word_counter > 1:
                            break
    return counter

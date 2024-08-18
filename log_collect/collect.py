import requests
from bs4 import BeautifulSoup
import re
import urllib.request
from pathlib import Path
import datetime
import time

def get_filtered_thread_urls(keywordsTRPG,keywordsOCL):
    thread_urls = set()
    for num in range(0,601,60):
        base_url = f'https://img.2chan.net/v.php?b,{num},1'  # 掲示板のURLに置き換えてください
        # print(base_url)
        # 掲示板のページを取得
        response = requests.get(base_url)
        
        # レスポンスのステータスコードが200 (OK) であることを確認
        if response.status_code != 200:
            print(f"Failed to retrieve page. Status code: {response.status_code}")
            return []

        # HTMLを解析
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # スレッドを含むタグを見つける
        # ここでは例として<a>タグを使用しているが、実際の構造に応じて調整が必要
        for a_tag in soup.find_all('a'):
            title = a_tag.get_text(strip=True)
            # print(title)
            if any(keyword in title for keyword in keywordsTRPG) and any(keyword in title for keyword in keywordsOCL):
                # スレッドのURLを取得
                thread_url = a_tag.get('href')
                thread_urls.add(thread_url)
    
    return thread_urls

def extract_filenames_from_thread(thread_url):
    # スレッドのページを取得
    response = requests.get(thread_url)
    
    # レスポンスのステータスコードが200 (OK) であることを確認
    if response.status_code != 200:
        print(f"Failed to retrieve page. Status code: {response.status_code}")
        return []
    # HTMLを解析
    soup = BeautifulSoup(response.text, 'html.parser')

    # # スレッドの内容を取得（例: <div class="post-content"> 内にスレッドの本文があると仮定）
    # content_div = soup.find('div',class_='ui-page-active')
    # if content_div is None:
    #     print("Content div not found.")
    #     return []

    # スレッドの本文を取得
    # content = content_div.get_text()
    # content=soup.body.div.get_text(" ")
    content=soup.body.find('div',class_='thre').get_text(" ")
    # print(content)
    # ファイル名を抽出するための正規表現パターン
    pattern = re.compile(r'(fu\d*\.[a-zA-Z]{3,4})|(f\d*\.[a-zA-Z]{3,4})', re.IGNORECASE)
    
    # 正規表現でファイル名を抽出
    filenames = pattern.findall(content)

    filenames = set([f"{match[0]}" for match in filenames])

    return  content,filenames

def getTRPGOCLlog():

    # 使用例

    keywordsTRPG = ['TRPG','ＴＲＰＧ']
    keywordsOCL = ['OCL','OCN','ＯＣＬ','ＯＣＮ']
    urls = get_filtered_thread_urls(keywordsTRPG,keywordsOCL)
    # urls.add("https://img.2chan.net/v.php?b.12236")# 該当記事なしテスト ステータスコードは200で帰ってくる
    logdir=Path("d:\\TRPGOCL_logs") #ひとまずDドライブ直下に展開　Linuxmacはしらん

    date = format(datetime.date.today(), '%Y%m%d')
    if urls:
        print("Found thread URLs:")
        for url in urls:
            # print(url)
            qs = urllib.parse.urlparse(url).query
            threurl=f"https://img.2chan.net/b/res/{qs[2:]}.htm"
            print(threurl)
            content,filenames = extract_filenames_from_thread(threurl)
            # filenames.add("fu00000.html")# 該当ファイルなしテスト 404エラーのためダウンロードオブジェクトがHTTPSErrorを送出
            if filenames:
                print("Found filenames:")
                for filename in filenames:
                    print(filename)
                    if filename.startswith("fu"):
                        fileurl='https://dec.2chan.net/up2/src/'+filename
                    else:
                        fileurl="https://dec.2chan.net/up/src/"+filename
                    Path.mkdir(logdir/date,exist_ok=True)
                    # _,res=urllib.request.urlretrieve(url, logdir/date/filename)

                    # ダウンロードする
                    try:
                        ret = urllib.request.urlopen(fileurl)
                    except Exception as e:
                        print(f"{e}")
                        errlog = re.sub(r'[\\/:*?"<>|]+','',url)
                        with open(str(logdir/date/errlog)+".log", mode="w") as f:
                            f.write(content)
                        continue

                    if ret.status != 200:
                        print(f"Failed to retrieve page. Status code: {ret.status}")
                        errlog = re.sub(r'[\\/:*?"<>|]+','',url)
                        with open(str(logdir/date/errlog)+".log", mode="w") as f:
                            f.write(content)
                    mem = ret.read()
                    
                    # ファイルへの保存
                    with open(str(logdir/date/filename), mode="wb") as f:
                        f.write(mem)
                    del mem

            else:
                print("No filenames found.")
    else:
        print("No threads found.")

def main():
    interval = 60
    while True:
        getTRPGOCLlog()
        print("次の回収は"+str((datetime.datetime.now()+ datetime.timedelta(seconds=interval)).time()))
        time.sleep(interval)

if __name__ == "__main__":
    main()
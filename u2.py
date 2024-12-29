import os
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pyodbc

url = "https://www.u2mtv.com/movie/allMovie/"
max_pages = 5
movieUrlList = []
movieData = []
img_folder = "movie_images"

# 取得電影連結
def movieUrl_data(url, current_page=1):
    if current_page > max_pages:
        print(f"已達到最大頁數限制（{max_pages} 頁），停止爬取。")
        return

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    #  獲取電影連結
    movies = soup.select("#movie_grid a")
    for movie in movies:
        url = "https://www.u2mtv.com" + movie.get("href")
        # movieUrlList.append(url)
        print(f"正在獲取: {url}")
        movie_data(url)

    # 檢查下一頁連結
    next_page = soup.select_one(".link_more_div")
    # print(next_page.find("a"))
    if next_page and next_page.find("a"):
        next_url = next_page.find("a").get("href")
        next_url = "https://www.u2mtv.com" + str(next_url)
        print(f"正在爬取:{next_url}")
        time.sleep(1)   # 延遲一秒，避免過度頻繁請求
        movieUrl_data(next_url, current_page + 1)

# 取得電影資料
def movie_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 獲取電影表單
    infos = soup.find_all("div", id="movie_info_main_div")
    
    for info in infos:
        # 電影名稱
        title = info.find("div", class_="title_div clearfix")
        title = title.h1.text.strip()
        # 根據分隔符號切割
        parts = title.split("\n")
        # 確保去掉左右多餘空白
        parts = [part.strip() for part in parts]
        # 結果
        chinese_title = parts[0] if len(parts) > 0 else ""
        english_title = parts[1] if len(parts) > 1 else ""

        # 電影圖片
        img = info.find("div", class_="thumbnail")
        img = img.img.get("src")
        save_image(img, chinese_title)

        # 如果圖片下載失敗，跳過該條目
        if not img:
            print(f"跳過圖片無法下載的電影：{chinese_title}")
            continue

        # 導演
        director = info.find("ul", class_="movie_info_direct_ul")
        director = [li.get_text() for li in director.select(".movie_info_direct_ul li")]

        # 演員
        actor = info.find("ul", class_="movie_info_actor_ul")
        actor = [li.get_text() for li in actor.select(".movie_info_actor_ul li")]

        #  年份
        year = info.find_all("span", class_="movie_info_table_content")
        year = year[0].text
        year = convert_to_gregorian(year)

        # 播放時間
        playTime = info.find_all("span", class_="movie_info_table_content")
        playTime = playTime[1].text

        # 分級 : 普遍級
        movieRate = info.find_all("span", class_="movie_info_table_content")
        movieRate = movieRate[2].text

        # 內容
        description = soup.select("div.movie_info_content_div p")[1].get_text()

        # 預告片
        iframe = soup.select_one("div.movie_info_content_div iframe")
        youtube = iframe.get("src") if iframe else "無預告片"

        data = {
            "中文電影名稱": str(chinese_title),
            "英文電影名稱" : str(english_title),
            "電影圖片" : str(img),
            "導演" : str(director),
            "演員" : str(actor),
            "上映年份" : str(year),
            "播放時間" : str(playTime),
            "分級" : str(movieRate),
            "內容" : str(description),
            "預告片" : str(youtube)
        }

        print(data)
        movieData.append(data)
        # print(movieData)

# 建立圖片資料夾
if not os.path.exists(img_folder):
    os.makedirs(img_folder)
# 存取圖片
def save_image(img_url, img_name):
    try:
        response = requests.get(img_url, stream=True)  # 使用 stream=True 下載大文件
        if response.status_code == 200:
            # 強制保存為 .jpg
            img_name = os.path.splitext(img_name)[0] + ".jpg"
            img_path = os.path.join(img_folder, img_name)
            with open(img_path, "wb") as img_file:
                img_file.write(response.content)
            print(f"圖片已保存：{img_path}")
            return img_name  # 返回保存的圖片名稱
        else:
            print(f"圖片下載失敗：{img_url}")
            return None
    except Exception as e:
        print(f"下載圖片時發生錯誤：{e}")
        return None     
# 丟入資料庫
def insert_to_mssql(data):
    conn_str = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=your_server;DATABASE=your_database;UID=your_user;PWD=your_password"
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # 插入資料
        sql = """
        INSERT INTO MovieData (ChineseTitle, EnglishTitle, ImgPath, Director, Actors, Year, PlayTime, Rating, Description, Youtube)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        for item in data:
            cursor.execute(sql, 
                           item["中文電影名稱"], 
                           item["英文電影名稱"], 
                           item["電影圖片"], 
                           ",".join(item["導演"]), 
                           ",".join(item["演員"]), 
                           item["上映年份"], 
                           item["播放時間"], 
                           item["分級"], 
                           item["內容"], 
                           item["預告片"])
        
        conn.commit()
        print("資料已成功插入至 MSSQL！")
    except Exception as e:
        print(f"插入資料時發生錯誤：{e}")
    finally:
        conn.close()
# 轉換日期
def convert_to_gregorian(minguo_date):
    """
    將民國日期轉換為西元日期。如果轉換失敗，返回空字串。
    """
    try:
        minguo_date_str = str(minguo_date)
        
        if len(minguo_date_str) == 7:  # 完整格式
            year = int(minguo_date_str[:3]) + 1911
            month = int(minguo_date_str[3:5])
            day = int(minguo_date_str[5:])
        elif len(minguo_date_str) == 5:  # 缺少日的格式
            year = int(minguo_date_str[:3]) + 1911
            month = int(minguo_date_str[3:5])
            day = 1  # 預設補為 1 日
        else:
            return ""  # 格式不符，返回空字串

        # 如果年份超過當前年份，推斷可能少加了100年
        current_year = datetime.now().year
        if year > current_year:
            year -= 100

        # 檢查日期是否有效
        date = datetime(year, month, day)
        return date.strftime("%Y/%m/%d")  # 格式化為 YYYY/MM/DD
    except Exception:
        return ""  # 任意錯誤時，返回空字串



# 啟動案子
movieUrl_data(url)

# # 插入資料
# insert_to_mssql(movieData)

 
# 測試用
# url = "https://www.u2mtv.com/movie/info/?mid=15142"
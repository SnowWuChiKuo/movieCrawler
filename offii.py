import os
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pyodbc
import logging
from typing import List, Dict, Union, Optional


url = "https://www.ofiii.com/filter?topic=4&sort=created_at"
max_pages = 5
movieUrlList = []
movieData = []
movieCategories=[]
img_folder = "movie_images"
img_url = "https://www.ofiii.com"
# # 測試用
# url = "https://www.ofiii.com/vod/72716/1/E1"

# MSSQL 連接字串
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=.\\sql2022;"  # 替換為您的伺服器名稱
    "DATABASE=MovieTicket;"  # 替換為您的資料庫名稱
    "UID=sa5;"  # 替換為您的使用者名稱
    "PWD=123456;"  # 替換為您的密碼
)


# 取得電影連結
def movieUrl_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    #  獲取電影連結
    a_tags = soup.find_all('a', class_='jsx-1549108632 content_item')

    # 要添加的字串
    prefix = "https://www.ofiii.com"

    # 在每個 href 前添加字串
    for a in a_tags:
        href = a.get('href')
        if href:  # 確保 href 存在
            new_href = prefix + href
            # print(new_href)  # 輸出新的網址
            # movieUrlList.append(new_href)
            print(f"正在獲取: {new_href}")
            movie_data(new_href)
    
    #  獲取電影分類
    categories = soup.find_all('div', class_="jsx-2145870150 options")[1]

    displayOrder = 5
    for category in categories:
        c = category.text.strip()
        data = {
            "Name": c,
            "DisplayOrder": displayOrder,
        }
        movieCategories.append(data)
        displayOrder += 5
    print(movieCategories)

# 取得電影資料
def movie_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 獲取電影表單
    infos = soup.find_all("div", class_="detail_section")
    # print(infos)
    
    for info in infos:
        # 電影名稱
        chinese_title = info.find("h1", class_="jsx-3862431936 title")
        chinese_title = chinese_title.text.strip()


        english_title = info.find("h2", class_="jsx-3862431936 subtitle_section")
        english_title = english_title.text.strip()

        # 年份
        year = info.find("a", class_="jsx-3862431936 list link")
        year = year.text.strip()

        # 播放時間
        playTime = info.find("span", class_="jsx-3862431936 list")
        playTime = playTime.text.strip()
        playTime = ''.join(filter(str.isdigit, playTime))

        # 分級
        movieRate = info.find_all("span", class_="jsx-3862431936 list")
        movieRate = movieRate[1].text.strip()

        # 內容
        description = info.find("p", class_="jsx-1531172110 description")
        description = description.text.strip()

        # 以下都使用這個進行尋找個別的內容
        tags_items = soup.find_all('div', class_='jsx-1531172110 tags_item')

        # 類型
        genre = []
        for item in tags_items:
            title = item.find('div', class_='jsx-1531172110 item_title')
            if title and title.get_text(strip=True) == '類型':
                # 找到類型標題後，提取所有的 <a> 標籤
                a_tags = item.find('div', class_='jsx-1531172110 item_content').find_all('a')
                # 提取每個 <a> 標籤中的文本
                genre = [a.get_text(strip=True) for a in a_tags]

        # 演員
        actor = []
        for item in tags_items:
            title = item.find('div', class_='jsx-1531172110 item_title')
            if title and title.get_text(strip=True) == '演員':
                # 找到演員標題後，提取所有的 <a> 標籤
                a_tags = item.find('div', class_='jsx-1531172110 item_content').find_all('a')
                # 提取每個 <a> 標籤中的文本
                actor = [a.get_text(strip=True) for a in a_tags]
        
        # 編劇

        # 導演
        director = []

        # 遍歷所有的 tags_item
        for item in tags_items:
            title = item.find('div', class_='jsx-1531172110 item_title')
            if title and title.get_text(strip=True) == '導演':
                # 找到導演標題後，提取所有的 <a> 標籤
                a_tags = item.find('div', class_='jsx-1531172110 item_content').find_all('a')
                # 提取每個 <a> 標籤中的文本
                director = [a.get_text(strip=True) for a in a_tags]


        # 國別
        country = []
        # country = info.find_all("div", class_="jsx-1531172110 item_content")
        # country = [tag.get_text(strip=True) for tag in country[5]]
        for item in tags_items:
            title = item.find('div', class_='jsx-1531172110 item_title')
            if title and title.get_text(strip=True) == '國別':
                # 找到導演標題後，提取所有的 <a> 標籤
                a_tags = item.find('div', class_='jsx-1531172110 item_content').find_all('a')
                # 提取每個 <a> 標籤中的文本
                country = [a.get_text(strip=True) for a in a_tags]

        # 語言
        lang = []
        # lang = info.find_all("div", class_="jsx-1531172110 item_content")
        # lang = [tag.get_text(strip=True) for tag in lang[6]]
        for item in tags_items:
            title = item.find('div', class_='jsx-1531172110 item_title')
            if title and title.get_text(strip=True) == '語言':
                # 找到導演標題後，提取所有的 <a> 標籤
                a_tags = item.find('div', class_='jsx-1531172110 item_content').find_all('a')
                # 提取每個 <a> 標籤中的文本
                lang = [a.get_text(strip=True) for a in a_tags]

        # 圖片
        image = soup.find("div", class_="jsx-3672361153")
        image = image.find("img").get("src")
        image = img_url + image
        save_image(image, chinese_title)

        # 如果圖片下載失敗，跳過該條目
        if not image:
            print(f"跳過圖片無法下載的電影：{chinese_title}")
            continue

        data = {
            "Title": chinese_title,
            # "英文電影名稱" : english_title,
            "PosterURL" : chinese_title + ".jpg",
            "Director" : director,
            "Cast" : actor,
            "ReleaseDate" : year,
            "RunTime" : playTime,
            "Description" : description, 
            "RatingId": movieRate, 
            "GenreId": genre
        }

        # print(data)
        movieData.append(data)
        # 插入資料庫
        insert_movie_data(movieData)
        print(movieData)
    
# movie_data(url)

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





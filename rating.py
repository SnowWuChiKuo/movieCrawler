import requests
from bs4 import BeautifulSoup
import pyodbc

# 全域變數
movieData = []  # 用於儲存電影分級資料
seen_rates = set()  # 用於追蹤已添加的分級
displayOrder = 5  # 全域變數，初始值為 5

def movieUrl_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 獲取電影連結
    a_tags = soup.find_all('a', class_='jsx-1549108632 content_item')

    # 要添加的字串
    prefix = "https://www.ofiii.com"

    # 在每個 href 前添加字串
    for a in a_tags:
        href = a.get('href')
        if href:  # 確保 href 存在
            new_href = prefix + href
            print(f"正在獲取: {new_href}")
            movie_data(new_href)  # 呼叫 movie_data 函式處理每個電影連結

def movie_data(url):
    global movieData, seen_rates, displayOrder  # 使用全域變數

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # 獲取電影表單
    infos = soup.find_all("div", class_="detail_section")

    for info in infos:
        # 分級
        movieRate = info.find_all("span", class_="jsx-3862431936 list")
        
        if len(movieRate) > 1:  # 確保有足夠的元素
            movieRate = movieRate[1].text.strip()
            
            # 檢查分級是否已存在
            if movieRate not in seen_rates:
                data = {
                    "Name": movieRate,
                    "DisplayOrder": displayOrder
                }
                movieData.append(data)  # 加入全域的 movieData 清單
                seen_rates.add(movieRate)  # 將新分級添加到集合中
                
                # 遞增 displayOrder
                displayOrder += 5

    print(movieData)  # 每次更新後輸出目前的 movieData

def insert_into_database():
    # MSSQL 連接字串
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=.\\sql2022;"
        "DATABASE=MovieTicket;"
        "UID=sa5;"
        "PWD=123456;"
    )
    
    try:
        # 建立連接
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # 插入資料到 Ratings 資料表
        insert_query = """
        INSERT INTO Ratings (Name, DisplayOrder)
        VALUES (?, ?)
        """
        
        # 批量插入資料
        for data in movieData:
            cursor.execute(insert_query, (data['Name'], data['DisplayOrder']))
        
        # 提交變更
        conn.commit()
        print("所有電影分級資料已成功插入資料庫。")

    except pyodbc.Error as e:
        print(f"資料庫錯誤: {e}")
    
    finally:
        # 關閉連接
        if 'conn' in locals():
            cursor.close()
            conn.close()

# 使用範例
url = "https://www.ofiii.com/filter?topic=4&sort=created_at"  # 替換為實際的 URL
movieUrl_data(url)  # 爬取電影資料
insert_into_database()  # 將資料插入資料庫

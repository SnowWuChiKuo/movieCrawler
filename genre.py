import requests
from bs4 import BeautifulSoup
import pyodbc
import logging

# 基本設定
url = "https://www.ofiii.com/filter?topic=4&sort=created_at"
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=.\\sql2022;"
    "DATABASE=MovieTicket;"
    "UID=sa5;"
    "PWD=123456;"
)

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def is_genre_exists_in_db(genre_name: str) -> bool:
    """
    檢查資料庫中是否已存在相同的 Genre。
    """
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM Genres WHERE Name = ?"
        cursor.execute(query, (genre_name,))
        result = cursor.fetchone()
        return result[0] > 0  # 如果計數大於 0，表示已存在
    except pyodbc.Error as e:
        logging.error(f"檢查 Genre 時發生錯誤: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

def insert_genre_data(genres):
    """
    插入電影類型資料到資料庫，避免重複插入。
    """
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        insert_query = "INSERT INTO Genres (Name, DisplayOrder) VALUES (?, ?)"
        for genre in genres:
            if is_genre_exists_in_db(genre['Name']):
                logging.info(f"跳過重複的類型: {genre['Name']}")
                continue
            try:
                cursor.execute(insert_query, (genre['Name'], genre['DisplayOrder']))
                conn.commit()
                logging.info(f"成功插入類型: {genre['Name']}")
            except Exception as e:
                conn.rollback()
                logging.error(f"插入類型 '{genre['Name']}' 時發生錯誤: {str(e)}")
    except Exception as e:
        logging.error(f"資料庫連接錯誤: {str(e)}")
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

def fetch_genres(url):
    """
    爬取電影類型資料。
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # 獲取電影分類
        categories = soup.find_all('div', class_="jsx-2145870150 options")[1]
        genres = []
        display_order = 5
        for category in categories:
            genre_name = category.text.strip()
            genres.append({"Name": genre_name, "DisplayOrder": display_order})
            display_order += 5

        logging.info(f"成功爬取到 {len(genres)} 個類型資料")
        return genres
    except Exception as e:
        logging.error(f"爬取電影類型資料時發生錯誤: {str(e)}")
        return []

def main():
    """
    主程序：爬取電影類型並插入資料庫。
    """
    genres = fetch_genres(url)
    if genres:
        insert_genre_data(genres)
    else:
        logging.warning("未找到任何電影類型資料")

if __name__ == "__main__":
    main()

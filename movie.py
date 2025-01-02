import os
import requests
from bs4 import BeautifulSoup
import logging
import pyodbc
from typing import List, Dict, Optional

# 基本設定
url = "https://www.ofiii.com/filter?topic=4&sort=created_at"
img_folder = "movie_images"
img_url = "https://www.ofiii.com"
movieData = []

# 資料庫連接字串
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=.\\sql2022;"
    "DATABASE=MovieTicket;"
    "UID=sa5;"
    "PWD=123456;"
)

def setup_logging():
    """設置日誌配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def save_image(img_url: str, img_name: str) -> Optional[str]:
    """下載並保存圖片"""
    try:
        response = requests.get(img_url, stream=True)
        if response.status_code == 200:
            img_name = os.path.splitext(img_name)[0] + ".jpg"
            img_path = os.path.join(img_folder, img_name)
            with open(img_path, "wb") as img_file:
                img_file.write(response.content)
            logging.info(f"圖片已保存：{img_path}")
            return img_name
        else:
            logging.error(f"圖片下載失敗：{img_url}")
            return None
    except Exception as e:
        logging.error(f"下載圖片時發生錯誤：{e}")
        return None

def get_rating_id(conn: pyodbc.Connection, rating_name: str) -> Optional[int]:
    """根據評級名稱查找對應的 RatingId"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Id FROM Ratings WHERE Name = ?", rating_name)
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        logging.error(f"查詢 Rating ID 時發生錯誤: {str(e)}")
        return None

def get_genre_id(conn: pyodbc.Connection, genre_name: str) -> Optional[int]:
    """根據類型名稱查找對應的 GenreId"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Id FROM Genres WHERE Name = ?", genre_name)
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        logging.error(f"查詢 Genre ID 時發生錯誤: {str(e)}")
        return None

def is_title_exists(conn: pyodbc.Connection, title: str) -> bool:
    """檢查電影標題是否已存在"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Movies WHERE Title = ?", title)
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        logging.error(f"檢查標題重複時發生錯誤: {str(e)}")
        return True

def movie_data(url: str) -> None:
    """爬取單部電影的詳細資訊"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        infos = soup.find_all("div", class_="detail_section")
        
        for info in infos:
            # 電影名稱
            chinese_title = info.find("h1", class_="jsx-3862431936 title")
            chinese_title = chinese_title.text.strip() if chinese_title else ""

            # 年份
            year = info.find("a", class_="jsx-3862431936 list")
            year = year.text.strip() if year else ""

            # 播放時間
            playTime = info.find("span", class_="jsx-3862431936 list")
            playTime = ''.join(filter(str.isdigit, playTime.text.strip())) if playTime else "0"

            # 分級
            movieRate = info.find_all("span", class_="jsx-3862431936 list")
            movieRate = movieRate[1].text.strip() if len(movieRate) > 1 else ""

            # 內容
            description = info.find("p", class_="jsx-1531172110 description")
            description = description.text.strip() if description else ""

            # 尋找所有標籤項目
            tags_items = soup.find_all('div', class_='jsx-1531172110 tags_item')

            # 類型
            genre = []
            # 演員
            actor = []
            # 導演
            director = []

            for item in tags_items:
                title = item.find('div', class_='jsx-1531172110 item_title')
                if not title:
                    continue
                
                title_text = title.get_text(strip=True)
                content_div = item.find('div', class_='jsx-1531172110 item_content')
                
                if title_text == '類型' and content_div:
                    genre = [a.get_text(strip=True) for a in content_div.find_all('a')]
                elif title_text == '演員' and content_div:
                    actor = [a.get_text(strip=True) for a in content_div.find_all('a')]
                elif title_text == '導演' and content_div:
                    director = [a.get_text(strip=True) for a in content_div.find_all('a')]

            # 圖片
            image_div = soup.find("div", class_="jsx-3672361153")
            if image_div and image_div.find("img"):
                image = image_div.find("img").get("src")
                image = img_url + image
                poster_filename = save_image(image, chinese_title)
            else:
                poster_filename = None

            if not poster_filename:
                logging.warning(f"跳過圖片無法下載的電影：{chinese_title}")
                continue

            # 構建電影資料
            data = {
                "Title": chinese_title,
                "PosterURL": poster_filename,
                "Director": director,
                "Cast": actor,
                "ReleaseDate": year,
                "RunTime": playTime,
                "Description": description,
                "RatingId": movieRate,
                "GenreId": genre
            }

            movieData.append(data)
            
    except Exception as e:
        logging.error(f"爬取電影資料時發生錯誤: {str(e)}")

def movieUrl_data(url: str) -> None:
    """爬取電影列表頁面"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # 獲取電影連結
        a_tags = soup.find_all('a', class_='jsx-1549108632 content_item')
        
        for a in a_tags:
            href = a.get('href')
            if href:
                new_href = img_url + href
                logging.info(f"正在獲取: {new_href}")
                movie_data(new_href)

    except Exception as e:
        logging.error(f"爬取電影列表時發生錯誤: {str(e)}")

def insert_movie_data(movies: List[Dict]) -> Dict[str, int]:
    """插入電影資料到資料庫"""
    stats = {'success': 0, 'failed': 0, 'skipped': 0}
    
    try:
        conn = pyodbc.connect(conn_str)
        
        for movie in movies:
            try:
                # 檢查標題是否重複
                if is_title_exists(conn, movie['Title']):
                    logging.info(f"電影 '{movie['Title']}' 已存在，跳過")
                    stats['skipped'] += 1
                    continue

                # 查找 RatingId
                rating_id = None
                if 'RatingId' in movie:
                    rating_id = get_rating_id(conn, movie['RatingId'])
                    if rating_id is None:
                        logging.warning(f"找不到評級 '{movie['RatingId']}' 的對應 ID")

                # 查找 GenreId (使用第一個類型)
                genre_id = None
                if 'GenreId' in movie and movie['GenreId']:
                    first_genre = movie['GenreId'][0] if isinstance(movie['GenreId'], list) else movie['GenreId']
                    genre_id = get_genre_id(conn, first_genre)
                    if genre_id is None:
                        logging.warning(f"找不到類型 '{first_genre}' 的對應 ID")

                # 處理導演和演員列表
                director_str = ', '.join(movie['Director']) if isinstance(movie['Director'], list) else str(movie['Director'])
                cast_str = ', '.join(movie['Cast']) if isinstance(movie['Cast'], list) else str(movie['Cast'])

                # 準備插入語句
                cursor = conn.cursor()
                insert_query = """
                INSERT INTO Movies 
                (Title, Description, Director, Cast, RunTime, ReleaseDate, PosterURL, RatingId, GenreId)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                # 執行插入
                cursor.execute(insert_query, (
                    movie['Title'],
                    movie['Description'],
                    director_str,
                    cast_str,
                    int(movie['RunTime']),
                    movie['ReleaseDate'],
                    movie['PosterURL'],
                    rating_id,
                    genre_id
                ))
                
                conn.commit()
                logging.info(f"成功插入電影: {movie['Title']}")
                stats['success'] += 1

            except Exception as e:
                conn.rollback()
                logging.error(f"插入電影 '{movie.get('Title', 'Unknown')}' 時發生錯誤: {str(e)}")
                stats['failed'] += 1

    except Exception as e:
        logging.error(f"資料庫連接錯誤: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

    logging.info(f"插入統計: {stats}")
    return stats

def main():
    """主程序"""
    setup_logging()
    
    # 建立圖片資料夾
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)
    
    try:
        # 爬取電影資料
        movieUrl_data(url)
        
        # 如果有電影資料，則插入資料庫
        if movieData:
            results = insert_movie_data(movieData)
            logging.info(f"資料處理完成: 成功={results['success']}, 失敗={results['failed']}, 跳過={results['skipped']}")
        else:
            logging.warning("沒有找到電影資料")
            
    except Exception as e:
        logging.error(f"程序執行錯誤: {str(e)}")

if __name__ == "__main__":
    main()
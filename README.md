# movieCrawler

## 請下載此檔案

git clone https://github.com/SnowWuChiKuo/movieCrawler

找地方開資料夾下載，需要用 Vscode 在進入此資料夾。

## 請安裝 python 主程式

https://www.python.org/downloads/

## 請安裝以下套件

- pip install requests
- pip install beautifulsoup4
- pip install pyodbc

## 啟動專案

python offii.py  
爬取整個網站，但不丟入資料庫，會下載圖片

python u2.py  
爬取整個網站，但不丟入資料庫，會下載圖片

python rating.py
爬取影片的分級，都會丟入資料庫

python genre.py
爬取影片的類型，都會丟入資料庫

python movie.py
爬取所有影片，並且丟入資料庫

python db.py
測試資料庫連線

請先測試資料庫連線狀況，再去個別的檔案進行修改。

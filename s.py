import random
import datetime

def generate_screenings_insert_sql(num_screenings=600, num_movies=60, num_theaters=15):
    """
    生成 SQL INSERT 語句，用於插入場次資料。

    Args:
        num_screenings: 場次數量。
        num_movies: 電影數量。
        num_theaters: 影廳數量。

    Returns:
        包含所有 INSERT 語句的字串。
    """

    sql_statements = []
    screening_id = 1
    start_date = datetime.date(2025, 1, 18)
    end_date = datetime.date(2025, 1, 31)
    today = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] # 今天的日期時間，格式化到毫秒

    for _ in range(num_screenings):
        movie_id = random.randint(1, num_movies)
        theater_id = random.randint(1, num_theaters)
        televising_date = start_date + datetime.timedelta(days=random.randint(0, (end_date - start_date).days))

        # 根據影廳調整開始時間
        start_hour = 9 + (theater_id - 1) * (40 / 60) # 每個影廳開始時間差40分鐘，換算成小時
        start_datetime = datetime.datetime(televising_date.year, televising_date.month, televising_date.day, int(start_hour), int((start_hour % 1) * 60) )

        #電影時間間隔2小時40分
        time_interval = datetime.timedelta(hours=2, minutes=40)
        start_datetime += time_interval * ((screening_id-1) // (num_theaters*num_movies) ) # 同一部電影在同一個影廳的間隔
        end_datetime = start_datetime + datetime.timedelta(hours=2, minutes=10)

        start_time_str = start_datetime.strftime("%H:%M:%S")
        end_time_str = end_datetime.strftime("%H:%M:%S")
        televising_str = televising_date.strftime("%Y-%m-%d")

        sql = f"INSERT [dbo].[Screenings] ([Id], [MovieId], [TheaterId], [Televising], [StartTime], [EndTime], [CreatedAt], [UpdatedAt]) VALUES ({screening_id}, {movie_id}, {theater_id}, CAST(N'{televising_str}' AS Date), CAST(N'{start_time_str}' AS Time), CAST(N'{end_time_str}' AS Time), CAST(N'{today}' AS DateTime), NULL)"
        sql_statements.append(sql)
        screening_id += 1


    return "\nGO\n".join(sql_statements) + "\nGO" # 使用換行符號和GO連接所有語句

def write_to_file(content, filename="screenings_insert.txt"):
    """
    將內容寫入檔案。
    """
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"SQL 語句已成功寫入 {filename} 檔案。")
    except Exception as e:
        print(f"寫入檔案時發生錯誤：{e}")

if __name__ == "__main__":
    sql_content = generate_screenings_insert_sql()
    write_to_file(sql_content)
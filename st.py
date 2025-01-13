import datetime

def generate_seat_status_insert_sql(num_screenings=600, seats_per_screening=190):
    """
    生成 SQL INSERT 語句，用於插入座位狀態資料。

    Args:
        num_screenings: 場次數量。
        seats_per_screening: 每個場次的座位數量。

    Returns:
        包含所有 INSERT 語句的字串。
    """

    sql_statements = []
    status_id = 1
    updated_at = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] # 今天的日期時間，格式化到毫秒

    for screening_id in range(1, num_screenings + 1):
        for seat_id in range(1, seats_per_screening + 1):
            sql = f"INSERT [dbo].[SeatStatus] ([Id], [ScreeningId], [SeatId], [Status], [UpdatedAt]) VALUES ({status_id}, {screening_id}, {seat_id}, N'可使用', CAST(N'{updated_at}' AS DateTime))"
            sql_statements.append(sql)
            status_id += 1

    return "\nGO\n".join(sql_statements) + "\nGO" # 使用換行符號和GO連接所有語句

def write_to_file(content, filename="seat_status_insert.txt"):
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
    sql_content = generate_seat_status_insert_sql()
    write_to_file(sql_content)
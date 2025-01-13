def generate_seats_insert_sql(num_theaters=15, num_rows=19, num_numbers=10, batch_size=100):
    """
    生成 SQL INSERT 語句，並在每 batch_size 筆語句後加入 GO。

    Args:
        num_theaters: 影廳數量。
        num_rows: 每個影廳的排數。
        num_numbers: 每一排的座位數量。
        batch_size: 每批 INSERT 語句的數量。

    Returns:
        包含所有 INSERT 語句和 GO 語句的字串。
    """

    sql_statements = []
    seat_id = 1
    counter = 0  # 用於計數已生成的語句數量

    for theater_id in range(1, num_theaters + 1):
        for row_num in range(1, num_rows + 1):
            for number in range(1, num_numbers + 1):
                sql = f"INSERT [dbo].[Seats] ([Id], [TheaterId], [Row], [Number], [IsDisabled]) VALUES ({seat_id}, {theater_id}, {row_num}, {number}, 0)"
                sql_statements.append(sql)
                seat_id += 1
                counter += 1

                # 每 batch_size 筆語句後加入 GO
                if counter % batch_size == 0:
                    sql_statements.append("GO")

    # 處理最後一批，如果數量不足 batch_size 也加入 GO
    if counter % batch_size != 0:
        sql_statements.append("GO")

    return "\n".join(sql_statements)

def write_to_file(content, filename="seats_insert.txt"):
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
    sql_content = generate_seats_insert_sql()
    write_to_file(sql_content)
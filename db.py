import pyodbc

try:
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=.\\sql2022;"
        "DATABASE=MovieTicket;"
        "UID=sa5;"
        "PWD=123456;"
    )
    
    conn = pyodbc.connect(conn_str)
    print("成功連接到資料庫！")
    
    # 在這裡執行您的 SQL 查詢或操作

except pyodbc.InterfaceError as e:
    print(f"連接錯誤: {e}")
except Exception as e:
    print(f"發生錯誤: {e}")
finally:
    if 'conn' in locals():
        conn.close()
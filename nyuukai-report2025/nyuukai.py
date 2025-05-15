import bottle
import sqlite3
from datetime import datetime,timedelta
from openpyxl import Workbook

conn = sqlite3.connect("sqlite.db", check_same_thread=False)

conn.execute("DROP TABLE IF EXISTS members")
conn.execute("""
CREATE TABLE IF NOT EXISTS members
(id integer primary key autoincrement,name text, line_name text,grade number, number text,
first_choice text, first_date text, first_time text, first_method text,
second_choice text, second_date text, second_time text, second_method text,
third_choice text, third_date text, third_time text, third_method text
)
""")
conn.commit()

application = bottle.Bottle()

@application.route("/")
def root():
    today_dt = datetime.now()  # datetime型
    tomorrow = (today_dt + timedelta(days=2)).strftime("%Y-%m-%d")
    max_date = "2025-05-13"
    return bottle.template("./static/reservation.html", {
        "tomorrow": tomorrow,
        "max_date": max_date
    })

@application.post("/check_availability")
def check_availability():
    choice = bottle.request.forms.get("choice")  # 局名
    date = bottle.request.forms.get("date")
    time = bottle.request.forms.get("time")

    cur = conn.cursor()
    sql_check = """
    SELECT * FROM members
    WHERE
        (first_choice = ? AND first_date = ? AND first_time = ?) OR
        (second_choice = ? AND second_date = ? AND second_time = ?) OR
        (third_choice = ? AND third_date = ? AND third_time = ?)
    """
    cur.execute(sql_check, (choice, date, time, choice, date, time, choice, date, time))
    existing = cur.fetchone()

    if existing:
        return {"status": "unavailable"}
    else:
        return {"status": "available"}

@application.post("/submit")
@bottle.view("submit")
def submit():
    name = bottle.request.params.name
    line_name = bottle.request.params.line_name
    grade = bottle.request.params.grade
    number = bottle.request.params.number
    first_choice = bottle.request.params.first_choice
    first_date = bottle.request.params.first_date
    first_time = bottle.request.params.first_time
    first_method = bottle.request.params.first_method
    second_choice = bottle.request.params.second_choice
    second_date = bottle.request.params.second_date
    second_time = bottle.request.params.second_time
    second_method = bottle.request.params.second_method
    third_choice = bottle.request.params.third_choice
    third_date = bottle.request.params.third_date
    third_time = bottle.request.params.third_time
    third_method = bottle.request.params.third_method

    try:
        first_date_obj = datetime.strptime(first_date, "%Y-%m-%d")
        formatted_first_date = first_date_obj.strftime("%Y年%m月%d日")
    except ValueError:
        return bottle.HTTPError(400, "第一希望の日付は「YYYY-MM-DD」の形式で入力してください。")

    formatted_second_date = ""
    if second_date:
        try:
            second_date_obj = datetime.strptime(second_date, "%Y-%m-%d")
            formatted_second_date = second_date_obj.strftime("%Y年%m月%d日")
        except ValueError:
            return bottle.HTTPError(400, "第二希望の日付は「YYYY-MM-DD」の形式で入力してください。")

    formatted_third_date = ""
    if third_date:
        try:
            third_date_obj = datetime.strptime(third_date, "%Y-%m-%d")
            formatted_third_date = third_date_obj.strftime("%Y年%m月%d日")
        except ValueError:
            return bottle.HTTPError(400, "第三希望の日付は「YYYY-MM-DD」の形式で入力してください。")

    cur = conn.cursor()

    # 任意の希望に関係なく、同じ時間帯がすでに予約されているか確認
    sql_check = """
    SELECT * FROM members
    WHERE
        (first_choice = ? AND first_date = ? AND first_time = ?) OR
        (second_choice = ? AND second_date = ? AND second_time = ?) OR
        (third_choice = ? AND third_date = ? AND third_time = ?)
    """

    cur.execute(sql_check, (first_choice, first_date, first_time,
                        first_choice, first_date, first_time,
                        first_choice, first_date, first_time))
    existing_first = cur.fetchone()

    if existing_first:
        return bottle.HTTPError(400, f"{formatted_first_date}の{first_time}の面談予約は既に埋まっています。")

    if second_time:
        cur.execute(sql_check, (second_choice, second_date, second_time,
                        second_choice, second_date, second_time,
                        second_choice, second_date, second_time))
        existing_second = cur.fetchone()

        if existing_second:
            return bottle.HTTPError(400, f"{formatted_second_date}の{second_time}の面談予約は既に埋まっています。")

    if third_time:
        cur.execute(sql_check, (third_choice, third_date, third_time,
                        third_choice, third_date, third_time,
                        third_choice, third_date, third_time))
        existing_third = cur.fetchone()

        if existing_third:
            return bottle.HTTPError(400, f"{formatted_third_date}の{third_time}の面談予約は既に埋まっています。")

    # データベースに登録
    sql_insert = """
    INSERT INTO members (name, line_name, grade, number, first_choice, first_date, first_time, first_method, second_choice, second_date, second_time, second_method, third_choice, third_date, third_time,third_method)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)"""
    conn.execute(sql_insert, (name, line_name ,grade ,number, first_choice, first_date, first_time, first_method, second_choice, second_date, second_time, second_method, third_choice, third_date,third_time,third_method))
    conn.commit()

    # Excelファイルの作成・更新
    wb = Workbook()
    ws = wb.active
    ws.title = "予約一覧"
    headers = ["ID", "氏名", "LINEの名前","学年","学籍番号","第一希望", "第一希望日付", "第一希望時間", "第一希望局形式","第二希望", "第二希望日付", "第二希望時間", "第二希望局形式", "第三希望", "第三希望日付","第二希望時間","第三希望形式" ]
    ws.append(headers)

    cur.execute("SELECT * FROM members ORDER BY first_date, first_time")
    rows = cur.fetchall()
    for row in rows:
        ws.append(row)

    file_path = "nyuukai-form2025.xlsx"
    wb.save(file_path)

    return {
        "name": name,
        "line_name": line_name,
        "first_choice": first_choice,
        "grade":grade,
        "number":number,
        "first_date": formatted_first_date,
        "first_time": first_time,
        "first_method":first_method,
        "second_choice": second_choice,
        "second_date": formatted_second_date,
        "second_time": second_time,
        "second_method":second_method,
        "third_choice": third_choice,
        "third_date":third_date,
        "third_time":third_time,
        "third_method": third_method,
        "file_path": file_path
    }
@application.get("/reservations")
def get_reservations():
    cur = conn.cursor()
    cur.execute("SELECT * FROM members ORDER BY first_date, first_time")
    rows = cur.fetchall()

    reservations = []
    for row in rows:
        reservations.append({
            "id": row[0], "name": row[1], "line_name": row[2],"grade":row[3],"number":row[4],
            "first_choice": row[5], "first_date": row[6], "first_time": row[7], "first_method": row[8],
            "second_choice": row[9], "second_date": row[10], "second_time": row[11], "second_method": row[12],
            "third_choice": row[13], "third_date": row[14], "third_time": row[15], "third_method": row[16]
        })

    return {"reservations": reservations}
@application.post("/delete_reservation")
def update_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "予約一覧"

    headers = ["ID", "氏名", "LINEの名前","学年","学籍番号", "第一希望", "第一希望日付", "第一希望時間", "第一希望形式",
               "第二希望", "第二希望日付", "第二希望時間", "第二希望形式",
               "第三希望", "第三希望日付", "第三希望時間", "第三希望形式"]
    ws.append(headers)

    cur = conn.cursor()
    cur.execute("SELECT * FROM members ORDER BY first_date, first_time")
    rows = cur.fetchall()

    for row in rows:
        ws.append(row)

    file_path = "nyuukai-form2025.xlsx"
    wb.save(file_path)

def delete_reservation():
    reservation_id = bottle.request.forms.get("id")

    cur = conn.cursor()
    cur.execute("DELETE FROM members WHERE id = ?", (reservation_id,))
    conn.commit()

    # **Excelの更新**
    update_excel()

    return {"status": "success", "message": "予約が削除されました。"}

@application.get("/sorted_reservations")
def get_sorted_reservations():
    cur = conn.cursor()

    # 仕事以外のデータのみ取得
    sql = """
    SELECT name, line_name, grade, number, first_choice AS department, first_date AS date, first_time AS time, first_method AS method
    FROM members
    WHERE name <> '仕事' AND first_choice IS NOT NULL AND first_date IS NOT NULL
    UNION ALL
    SELECT name, line_name, grade, number, second_choice AS department, second_date, second_time, second_method
    FROM members
    WHERE name <> '仕事' AND second_choice IS NOT NULL AND second_date IS NOT NULL
    UNION ALL
    SELECT name, line_name, grade, number, third_choice AS department, third_date, third_time, third_method
    FROM members
    WHERE name <> '仕事' AND third_choice IS NOT NULL AND third_date IS NOT NULL
    ORDER BY department, date, time
    """

    cur.execute(sql)
    rows = cur.fetchall()

    # データ変換
    sorted_reservations = [
        {
            "name": row[0],
            "line_name": row[1],
            "grade": row[2],
            "number": row[3],
            "department": row[4] if row[4] else "",
            "date": row[5] if row[5] else "",
            "time": row[6] if row[6] else "",
            "method": row[7] if row[7] else "",
        }
        for row in rows
    ]

    return {"sorted_reservations": sorted_reservations}

@application.get("/filtered_sorted_reservations")
def get_filtered_sorted_reservations():
    department = bottle.request.query.department.strip()

    if not department:
        return {"sorted_reservations": []}

    cur = conn.cursor()

    # 仕事以外のデータのみ取得
    sql = """
    SELECT name, line_name, grade, number, first_choice AS department, first_date AS date, first_time AS time, first_method AS method
    FROM members
    WHERE name <> '仕事' AND first_choice = ? AND first_date IS NOT NULL
    UNION ALL
    SELECT name, line_name, grade, number, second_choice AS department, second_date, second_time, second_method
    FROM members
    WHERE name <> '仕事' AND second_choice = ? AND second_date IS NOT NULL
    UNION ALL
    SELECT name, line_name, grade, number, third_choice AS department, third_date, third_time, third_method
    FROM members
    WHERE name <> '仕事' AND third_choice = ? AND third_date IS NOT NULL
    ORDER BY department, date, time
    """

    cur.execute(sql, (department, department, department))
    rows = cur.fetchall()

    # データ変換
    sorted_reservations = [
        {
            "name": row[0],
            "line_name": row[1],
            "grade": row[2],
            "number": row[3],
            "department": row[4] if row[4] else "",
            "date": row[5] if row[5] else "",
            "time": row[6] if row[6] else "",
            "method": row[7] if row[7] else "",
        }
        for row in rows
    ]

    return {"sorted_reservations": sorted_reservations}



@application.route("/sorted_reservations_page")
def sorted_reservations_page():
    return bottle.static_file("sorted_reservations.html", root="./static")

@application.get("/search_reservation")
def search_reservation():
    number = bottle.request.query.number.strip()

    cur = conn.cursor()
    sql = """
        SELECT '第一希望' AS choice_type, name, first_choice AS department, first_date AS date, first_time AS time
        FROM members WHERE number = ? AND first_date IS NOT NULL
        UNION ALL
        SELECT '第二希望', name, second_choice, second_date, second_time
        FROM members WHERE number = ? AND second_date IS NOT NULL
        UNION ALL
        SELECT '第三希望', name, third_choice, third_date, third_time
        FROM members WHERE number = ? AND third_date IS NOT NULL
    """
    cur.execute(sql, (number, number, number))
    rows = cur.fetchall()

    reservations = [
        {"choice_type": row[0], "name": row[1], "department": row[2], "date": row[3], "time": row[4]}
        for row in rows
    ]

    return {"reservations": reservations if reservations else None}



@application.post("/update_reservation")
def update_reservation():
    data = bottle.request.json
    number = data.get("number")
    name = data.get("name")
    choice = data.get("choice")  # "first", "second", "third" のいずれか
    new_date = data.get("new_date")
    new_time = data.get("new_time")


    if choice not in ["first", "second", "third"]:
        return {"message": "不正な希望の選択です"}

    cur = conn.cursor()

    # 変更する希望の局名を取得
    sql_get_choice = f"SELECT {choice}_choice FROM members WHERE number = ?"
    cur.execute(sql_get_choice, (number,))
    row = cur.fetchone()

    if not row:
        return {"message": "該当の予約が見つかりません"}

    selected_choice = row[0]  # 変更する局名

    # **リスケジュール前に、変更対象の局で日程被りがないかチェック**
    sql_check = """
    SELECT * FROM members
    WHERE
        (first_choice = ? AND first_date = ? AND first_time = ?) OR
        (second_choice = ? AND second_date = ? AND second_time = ?) OR
        (third_choice = ? AND third_date = ? AND third_time = ?)
    """
    cur.execute(sql_check, (selected_choice, new_date, new_time, selected_choice, new_date, new_time, selected_choice, new_date, new_time))
    existing = cur.fetchone()

    if existing:
        return {"message": f"{selected_choice} の {new_date} {new_time} はすでに予約されています。他の時間を選択してください"}

    # **希望の種類（第一・第二・第三）に応じてデータを更新**
    sql_update = f"""
    UPDATE members
    SET {choice}_date = ?, {choice}_time = ?
    WHERE number = ? AND {choice}_date IS NOT NULL
    """
    cur.execute(sql_update, (new_date, new_time, number))

    conn.commit()
    return {"message": f"{selected_choice} の予約を {new_date} の {new_time} に変更しました"}

@application.route("/reschedule_page")
def reschedule_page():
    today_dt = datetime.now()  # 現在の日付
    tomorrow = (today_dt + timedelta(days=2)).strftime("%Y-%m-%d")
    max_date = "2025-05-13"  # 最大日程の指定

    return bottle.template("./static/reschedule.html", {
        "tomorrow": tomorrow,
        "max_date": max_date
    })


@application.route("/admin_page")
def admin_page():
    return bottle.static_file("admin.html", root="./static")

@application.get("/admin_reservations")
def admin_reservations():
    cur = conn.cursor()
    cur.execute("SELECT * FROM members ORDER BY id DESC")
    rows = cur.fetchall()

    reservations = []
    for row in rows:
        reservations.append({
            "id": row[0], "name": row[1], "line_name": row[2],"grade":row[3],"number":row[4],
            "first_choice": row[5], "first_date": row[6], "first_time": row[7], "first_method": row[8],
            "second_choice": row[9], "second_date": row[10], "second_time": row[11], "second_method": row[12],
            "third_choice": row[13], "third_date": row[14], "third_time": row[15], "third_method": row[16]
        })
    return {"reservations": reservations}

@application.post("/admin_delete")
def admin_delete():
    reservation_id = bottle.request.forms.get("id")

    cur = conn.cursor()
    cur.execute("DELETE FROM members WHERE id = ?", (reservation_id,))
    conn.commit()
    return {"status": "success", "message": f"ID {reservation_id} の予約を削除しました"}

@application.post("/admin_update")
def admin_update():
    data = bottle.request.json
    reservation_id = data.get("id")
    column = data.get("column")
    value = data.get("value")

    if column not in [
        "name", "line_name","grade","number", "first_choice", "first_date", "first_time", "first_method",
        "second_choice", "second_date", "second_time", "second_method",
        "third_choice", "third_date", "third_time", "third_method"
    ]:
        return {"status": "error", "message": "変更対象の項目が無効です。"}

    cur = conn.cursor()
    sql = f"UPDATE members SET {column} = ? WHERE id = ?"
    cur.execute(sql, (value, reservation_id))
    conn.commit()

    return {"status": "success", "message": f"ID {reservation_id} の {column} を更新しました。"}

@application.get("/reservations_by_department")
def reservations_by_department():
    department = bottle.request.query.department

    cur = conn.cursor()
    sql = """
    SELECT id, name, line_name, grade, number, '第一希望' AS priority, first_date AS date, first_time AS time, first_method AS method
    FROM members WHERE first_choice = ? AND name = '仕事' AND first_date IS NOT NULL
    UNION ALL
    SELECT id, name, line_name, grade, number, '第二希望', second_date, second_time, second_method
    FROM members WHERE second_choice = ? AND name = '仕事' AND second_date IS NOT NULL
    UNION ALL
    SELECT id, name, line_name, grade, number, '第三希望', third_date, third_time, third_method
    FROM members WHERE third_choice = ? AND name = '仕事' AND third_date IS NOT NULL
    """

    cur.execute(sql, (department, department, department))
    rows = cur.fetchall()

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "name": row[1],
            "line_name": row[2],
            "grade": row[3],
            "number": row[4],
            "priority": row[5],
            "date": row[6],
            "time": row[7],
            "method": row[8],
        })
    return {"reservations": result}

@application.post("/admin_update_priority")
def admin_update_priority():
    data = bottle.request.json
    id = data.get("id")
    column = data.get("column")  # "date", "time", "method"
    value = data.get("value")
    priority = data.get("priority")

    prefix = {
        "第一希望": "first",
        "第二希望": "second",
        "第三希望": "third"
    }.get(priority)

    if not prefix:
        return {"message": "無効な希望種別です"}

    db_col = f"{prefix}_{column}"

    cur = conn.cursor()
    cur.execute(f"UPDATE members SET {db_col} = ? WHERE id = ?", (value, id))
    conn.commit()

    return {"message": f"ID {id} の {priority}の{column} を更新しました。"}

@application.post("/admin_delete_priority")
def admin_delete_priority():
    id = bottle.request.forms.get("id")
    priority = bottle.request.forms.get("priority")

    prefix = {
        "第一希望": "first",
        "第二希望": "second",
        "第三希望": "third"
    }.get(priority)

    if not prefix:
        return {"message": "無効な希望種別です"}

    cur = conn.cursor()
    cur.execute(f"""
        UPDATE members
        SET {prefix}_choice = NULL,
            {prefix}_date = NULL,
            {prefix}_time = NULL,
            {prefix}_method = NULL
        WHERE id = ?
    """, (id,))
    conn.commit()

    return {"message": f"ID {id} の {priority}希望を削除しました。"}

@application.route("/department_admin")
def department_admin():
    return bottle.static_file("department_admin.html", root="./static")

@application.route("/admin_schedule_work")
def admin_schedule_work_page():
    return bottle.static_file("admin_schedule_work.html", root="./static")

@application.post("/admin_register_work")
def admin_register_work():
    data = bottle.request.json
    department = data.get("department")
    date = data.get("date")
    times = data.get("times", [])

    cur = conn.cursor()

    # 各時間を登録
    for time in times:
        # 既存の重複チェック
        sql_check = """
        SELECT * FROM members
        WHERE first_choice = ? AND first_date = ? AND first_time = ?
        """
        cur.execute(sql_check, (department, date, time))
        existing = cur.fetchone()

        if existing:
            continue  # 既に登録済みの場合スキップ

        # 仕事のダミー登録
        sql_insert = """
        INSERT INTO members (name, line_name, grade, number,
                             first_choice, first_date, first_time, first_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(sql_insert, ("仕事", "", 0, "job", department, date, time, "対面"))

    conn.commit()
    return {"message": f"{len(times)} 件の時間帯を {department} に登録しました！"}

@application.get("/available_times")
def available_times():
    choice = bottle.request.query.choice
    date = bottle.request.query.date

    # 時間帯一覧（共通）
    all_times = [
        "08:30", "09:00", "09:30", "10:00", "10:30", "11:00",
        "11:30", "12:00", "12:30", "13:00", "13:30", "14:00",
        "14:30", "15:00", "15:30", "16:00", "16:30", "17:00",
        "17:30", "18:00", "18:30", "19:00", "19:30", "20:00",
        "20:30", "21:00", "21:30", "22:00", "22:30", "23:00"
    ]

    cur = conn.cursor()
    sql = """
    SELECT first_time FROM members WHERE first_choice = ? AND first_date = ?
    UNION
    SELECT second_time FROM members WHERE second_choice = ? AND second_date = ?
    UNION
    SELECT third_time FROM members WHERE third_choice = ? AND third_date = ?
    """
    cur.execute(sql, (choice, date, choice, date, choice, date))
    reserved_times = [row[0] for row in cur.fetchall() if row[0]]

    available = [time for time in all_times if time not in reserved_times]

    return {"available_times": available}



if __name__ == "__main__":
    application.run(host='localhost', port=8080)

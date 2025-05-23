import sqlite3

import requests
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/datagen')
def generate_data():
    conn = sqlite3.connect("user_data.sqlite")
    cursor = conn.cursor()
    user_list = []
    try:
        with open("sql_statement/init_table.sql", "r") as f:
            cursor.executescript(f.read())
            conn.commit()
        data = requests.get("https://dummyjson.com/users").json()
        for user in data["users"]:
            user_list.append((
                user["firstName"] + user["lastName"],
                user["birthDate"],
                user["gender"],
                user["email"],
                user["phone"],
                user["address"]["address"],
                user["address"]["city"],
                user["address"]["state"],
                user["address"]["postalCode"],
                user["university"],
                user["company"]["title"]
            ))
        with open("sql_statement/insert_user.sql", "r") as f:
            script = f.read()
            cursor.executemany(script, user_list)
            conn.commit()
            print(f"Successfully insert {len(user_list)} numbers of data")

    except sqlite3.Error as e:
        print("An error has occurred: ", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
        return "<p>Data has been generated</p>"

@app.route("/user")
def user_info():
    conn = sqlite3.connect("user_data.sqlite")
    cursor = conn.cursor()
    user_id = int(request.args.get("id"))
    if user_id < 1 or user_id > 30:
        return "Error: User not found"
    with open("sql_statement/query_user.sql", "r") as f:
        cursor.execute(f.read(), [user_id])
        data = cursor.fetchone()
        conn.close()
        return render_template("user_page.html",
                               full_name = data[1],
                               birthday = data[2],
                               gender = data[3],
                               email = data[4],
                               phone = data[5],
                               location = f"{data[6]} {data[7]}, {data[8]} {data[9]}",
                               uni = data[10],
                               title = data[11]
                               )



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

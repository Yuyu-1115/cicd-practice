import sqlite3

import requests
from flask import Flask, request, render_template, redirect, url_for, flash

app = Flask(__name__)


@app.route("/")
def home_page():
    return redirect(url_for("user_login"))

@app.route("/datagen")
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
                user["company"]["title"],
                user["password"]
            ))
        with open("sql_statement/insert_user.sql", "r") as f:
            script = f.read()
            cursor.executemany(script, user_list)
            conn.commit()

    except sqlite3.Error as e:
        print("An error has occurred: ", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
        return f"Successfully insert {len(user_list)} numbers of data"


# A vulnerability that pass user's credential via GET method
@app.route("/login")
def user_login():
    return render_template("login_page.html")

@app.route("/auth")
def authentication():
    query = f"SELECT id FROM users WHERE email == '{request.args.get("email")}' AND password == '{request.args.get("password")}'"
    conn = sqlite3.connect("user_data.sqlite")
    cursor = conn.cursor()
    try:
       cursor.execute(query)
       result = cursor.fetchone()
       conn.close()
       if result:
           return redirect(url_for("user_info", id=result[0]))
       else:
           return redirect(url_for("user_login"))
    except sqlite3.Error as e:
        print("An error has occurred: ", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


# A vulnerability that doesn't authenticate before showing user's information
@app.route("/user")
def user_info():
    conn = sqlite3.connect("user_data.sqlite")
    cursor = conn.cursor()
    user_id = int(request.args.get("id"))
    if user_id < 1 or user_id > 30:
        return "Error: User not found"
    try:
        with open("sql_statement/query_user.sql", "r") as f:
            cursor.execute(f.read(), [user_id])
            data = cursor.fetchone()[:-1]
            conn.close()
            return render_template("user_page.html",
                                   full_name=data[1],
                                   birthday=data[2],
                                   gender=data[3],
                                   email=data[4],
                                   phone=data[5],
                                   location=f"{data[6]} {data[7]}, {data[8]} {data[9]}",
                                   uni=data[10],
                                   title=data[11]
                                   )
    except sqlite3.Error as e:
        print("An error has occurred: ", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run()


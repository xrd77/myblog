import pymysql
from datetime import date

from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "ylan-blog-2026-secret"

try:
    from db_config import DB_CONFIG
except ImportError:
    raise SystemExit(
        "缺少 db_config.py：请把 db_config.example.py 复制一份改名为 db_config.py，"
        "并填入你自己的数据库用户名和密码。"
    )


@app.route("/")
def home():
    """首页：只展示最新 3 篇文章"""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute(
            """
            select posts.*, users.username as author_name
            from posts
            left join users on posts.author_id = users.id
            order by posts.id desc
            limit 3
            """
        )
        posts = cur.fetchall()
    conn.close()
    return render_template("index.html", posts=posts)


@app.route("/posts")
def posts_page():
    """文章页：展示全部文章"""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute(
            """
            select posts.*, users.username as author_name
            from posts
            left join users on posts.author_id = users.id
            order by posts.id desc
            """
        )
        posts = cur.fetchall()
    conn.close()
    return render_template("posts.html", posts=posts)


@app.route("/post/<int:post_id>")
def post_detail(post_id):
    """文章详情"""
    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute(
            """
            select posts.*, users.username as author_name
            from posts
            left join users on posts.author_id = users.id
            where posts.id = %s
            """,
            (post_id,),
        )
        post = cur.fetchone()
    conn.close()
    if post is None:
        return "文章不存在", 404
    return render_template("post.html", post=post)


@app.route("/new", methods=["GET", "POST"])
def new_post():
    """写文章：未登录不能发"""
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        today = date.today().isoformat()
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute(
                "insert into posts (title,content,date,author_id) values (%s,%s,%s,%s)",
                (title, content, today, session["user_id"]),
            )
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("new.html")


@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    """编辑文章：只有作者本人能改"""
    if "user_id" not in session:
        return redirect("/login")

    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("select * from posts where id = %s", (post_id,))
        post = cur.fetchone()

    if post is None:
        conn.close()
        return "文章不存在", 404
    if post["author_id"] != session["user_id"]:
        conn.close()
        return "这不是你的文章，不能修改", 403

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        today = date.today().isoformat()
        with conn.cursor() as cur:
            cur.execute(
                """
                update posts
                set title = %s, content = %s, date = %s
                where id = %s
                """,
                (title, content, today, post_id),
            )
        conn.commit()
        conn.close()
        return redirect(f"/post/{post_id}")

    conn.close()
    return render_template("edit.html", post=post)


@app.route("/delete/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    """删除文章：只有作者本人能删"""
    if "user_id" not in session:
        return redirect("/login")

    conn = pymysql.connect(**DB_CONFIG)
    with conn.cursor() as cur:
        cur.execute("select author_id from posts where id = %s", (post_id,))
        row = cur.fetchone()

        if row is None:
            conn.close()
            return "文章不存在", 404
        if row["author_id"] != session["user_id"]:
            conn.close()
            return "这不是你的文章，不能删除", 403

        cur.execute("delete from posts where id = %s", (post_id,))
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("select * from users where username = %s", (username,))
            user = cur.fetchone()
        conn.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            return "用户名或密码不对，请返回重试"

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect("/")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password2 = request.form["password2"]

        if password != password2:
            return "两次输入的密码不一致，请返回重新填写"

        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("select id from users where username = %s", (username,))
            if cur.fetchone() is not None:
                conn.close()
                return "这个用户名已经有人用了，换一个吧"

            cur.execute(
                "insert into users (username,password_hash,created_at) values (%s,%s,%s)",
                (username, generate_password_hash(password), date.today().isoformat()),
            )
        conn.commit()
        conn.close()
        return redirect("/login")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)

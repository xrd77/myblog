import pymysql

# 这个文件是模板：复制一份改名为 db_config.py，再填入你自己的数据库信息。
# db_config.py 已经在 .gitignore 里，不会被上传到 GitHub。
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "你的数据库用户名",
    "password": "你的数据库密码",
    "database": "blog",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

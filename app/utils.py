import pymysql
import os

from dotenv import load_dotenv

load_dotenv()

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "user": os.getenv("MYSQL_USER", "arxiv"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "arxiv"),
    "charset": "utf8mb4"
}


def get_mysql_conn():
    return pymysql.connect(**MYSQL_CONFIG)


def mark_paper(user_id, doi, is_favorite=False, note=None, rating=None):
    """用户对论文的收藏/评分/笔记操作"""
    conn = get_mysql_conn()
    cursor = conn.cursor()

    # 找到论文的主键 id
    cursor.execute("SELECT id FROM arxiv_papers WHERE doi=%s", (doi,))
    paper = cursor.fetchone()
    if not paper:
        conn.close()
        return False

    paper_id = paper[0]

    sql = """
    INSERT INTO user_paper_marks (user_id, paper_id, is_favorite, note, rating)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        is_favorite=VALUES(is_favorite),
        note=VALUES(note),
        rating=VALUES(rating),
        updated_at=CURRENT_TIMESTAMP
    """
    cursor.execute(sql, (user_id, paper_id, is_favorite, note, rating))
    conn.commit()
    cursor.close()
    conn.close()
    return True

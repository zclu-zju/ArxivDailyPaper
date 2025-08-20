from fastapi import FastAPI, Query, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
import arxiv
from utils import *

from dotenv import load_dotenv

load_dotenv()


# ---------- 数据模型 ----------
class Paper(BaseModel):
    doi: str
    url: str
    title: str
    authors: List[str]
    subjects: List[str]
    summary: str


class PaperMark(BaseModel):
    user_id: int
    doi: str
    is_favorite: Optional[bool] = False
    note: Optional[str] = None
    rating: Optional[int] = None


app = FastAPI(title="Arxiv Papers API", version="1.0")


@app.get("/papers/", response_model=List[Paper])
def get_papers(page: int = 1, page_size: int = 20, search: Optional[str] = Query(None)):
    """分页获取抓取的论文列表，可搜索标题/作者/摘要"""
    conn = get_mysql_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    offset = (page - 1) * page_size
    if search:
        sql = """SELECT * FROM arxiv_papers WHERE 
                 title LIKE %s OR authors LIKE %s OR summary LIKE %s
                 ORDER BY created_at DESC LIMIT %s OFFSET %s"""
        cursor.execute(sql, (f"%{search}%", f"%{search}%", f"%{search}%", page_size, offset))
    else:
        sql = "SELECT * FROM arxiv_papers ORDER BY created_at DESC LIMIT %s OFFSET %s"
        cursor.execute(sql, (page_size, offset))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        Paper(
            doi=row["doi"],
            url=row["url"],
            title=row["title"],
            authors=row["authors"].split(",") if row["authors"] else [],
            subjects=row["subjects"].split(",") if row["subjects"] else [],
            summary=row["summary"],
        )
        for row in rows
    ]


@app.get("/papers/{doi}", response_model=Paper)
def get_paper_detail(doi: str):
    """获取文章详细信息"""
    conn = get_mysql_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM arxiv_papers WHERE doi=%s", (doi,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Paper not found")
    return Paper(
        doi=row["doi"],
        url=row["url"],
        title=row["title"],
        authors=row["authors"].split(",") if row["authors"] else [],
        subjects=row["subjects"].split(",") if row["subjects"] else [],
        summary=row["summary"],
    )


@app.post("/papers/mark/")
def mark_paper_api(mark: PaperMark):
    """用户收藏/评分/笔记"""
    success = mark_paper(mark.user_id, mark.doi, mark.is_favorite, mark.note, mark.rating)
    if not success:
        raise HTTPException(status_code=404, detail="Paper not found")
    return {"status": "success"}


@app.get("/papers/user/{user_id}/favorites/", response_model=List[Paper])
def get_user_favorites(user_id: int):
    """获取用户收藏/评分过的论文"""
    conn = get_mysql_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = """
    SELECT p.* FROM arxiv_papers p 
    JOIN user_paper_marks m ON p.id=m.paper_id 
    WHERE m.user_id=%s AND m.is_favorite=1
    ORDER BY m.updated_at DESC
    """
    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        Paper(
            doi=row["doi"],
            url=row["url"],
            title=row["title"],
            authors=row["authors"].split(",") if row["authors"] else [],
            subjects=row["subjects"].split(",") if row["subjects"] else [],
            summary=row["summary"],
        )
        for row in rows
    ]


@app.get("/papers/user/{user_id}/marks/", response_model=List[Paper])
def get_user_marks(user_id: int):
    """获取用户对论文的标记信息"""
    conn = get_mysql_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = """
    SELECT p.* FROM arxiv_papers p 
    JOIN user_paper_marks m ON p.id=m.paper_id 
    WHERE m.user_id=%s
    ORDER BY m.updated_at DESC
    """
    cursor.execute(sql, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        Paper(
            doi=row["doi"],
            url=row["url"],
            title=row["title"],
            authors=row["authors"].split(",") if row["authors"] else [],
            subjects=row["subjects"].split(",") if row["subjects"] else [],
            summary=row["summary"],
        )
        for row in rows
    ]


@app.get("/papers/category/{category}", response_model=List[Paper])
def get_papers_by_category(category: str, page: int = 1, page_size: int = 20):
    """获取指定学科的论文"""
    conn = get_mysql_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    offset = (page - 1) * page_size
    sql = "SELECT * FROM arxiv_papers WHERE subjects LIKE %s ORDER BY created_at DESC LIMIT %s OFFSET %s"
    cursor.execute(sql, (f"%{category}%", page_size, offset))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        Paper(
            doi=row["doi"],
            url=row["url"],
            title=row["title"],
            authors=row["authors"].split(",") if row["authors"] else [],
            subjects=row["subjects"].split(",") if row["subjects"] else [],
            summary=row["summary"],
        )
        for row in rows
    ]


@app.get("/papers/category_counts/")
def get_category_counts():
    """获取每个学科的论文数量"""
    conn = get_mysql_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT subjects FROM arxiv_papers"
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    counts = {}
    for row in rows:
        if not row["subjects"]:
            continue
        for subject in row["subjects"].split(","):
            subject = subject.strip()
            counts[subject] = counts.get(subject, 0) + 1
    return counts


@app.get("/arxiv/search/", response_model=List[Paper])
def search_arxiv(query: str, max_results: int = 10):
    """使用 arxiv pypi 搜索最新论文"""
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results)
    results = []
    for r in client.results(search):
        results.append(
            Paper(
                doi=r.get_short_id(),
                url=r.entry_id,
                title=r.title.strip(),
                authors=[a.name for a in r.authors],
                subjects=[t for t in r.categories],
                summary=r.summary.strip(),
            )
        )
    return results

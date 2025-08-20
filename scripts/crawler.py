import json
from requests import Session
from lxml.etree import HTML
import redis
import pymysql
import arxiv

from notice import notice
from dotenv import load_dotenv

load_dotenv()

REDIS_CONFIG = {
    "host": "127.0.0.1",
    "port": 6379,
    "password": 123456,
    "db": 0,
    "decode_responses": True
}

MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "user": "arxiv",
    "password": "3PbXaRFeKPRtpjfF",
    "database": "arxiv",
    "charset": "utf8mb4"
}

xpath_config = {
    'block1': '//*[@id="articles"]/dt',
    'abstract': './a[@title="Abstract"]'
}


def get_mysql_conn():
    return pymysql.connect(**MYSQL_CONFIG)


def check_and_create_table():
    """创建论文主表"""
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS arxiv_papers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            doi VARCHAR(255) UNIQUE,
            url VARCHAR(500),
            title TEXT,
            authors TEXT,
            subjects TEXT,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    conn.commit()
    cursor.close()
    conn.close()


def check_and_create_user_table():
    """创建用户标记表"""
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_paper_marks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            paper_id INT NOT NULL,
            is_favorite BOOLEAN DEFAULT FALSE COMMENT '是否收藏',
            note TEXT COMMENT '用户笔记',
            rating INT DEFAULT NULL COMMENT '论文评分(1-5)',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_user_paper (user_id, paper_id),
            FOREIGN KEY (paper_id) REFERENCES arxiv_papers(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    conn.commit()
    cursor.close()
    conn.close()


def insert_mysql_bulk(data_list):
    """批量插入或更新论文数据"""
    if not data_list:
        return

    conn = get_mysql_conn()
    cursor = conn.cursor()
    sql = """
    INSERT INTO arxiv_papers (doi, url, title, authors, subjects, summary)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        title=VALUES(title), 
        authors=VALUES(authors), 
        subjects=VALUES(subjects),
        summary=VALUES(summary)
    """
    values = [
        (
            data['doi'],
            data['url'],
            data['title'],
            ','.join(data['authors']),
            ','.join(data['subjects']),
            data['summary']
        )
        for data in data_list
    ]
    cursor.executemany(sql, values)
    conn.commit()
    cursor.close()
    conn.close()


def save_or_skip_to_redis(r, block):
    """检查 Redis 去重，保存新论文"""
    if r.hexists("arxiv_papers", block['doi']):
        return False
    r.hset("arxiv_papers", block['doi'], json.dumps(block))
    return True


def get_id_list(url):
    """抓取 recent 页面的所有 doi"""
    session = Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/96.0.4664.110 Safari/537.36'
    })
    content = session.get(url).text
    html = HTML(content)
    block1 = html.xpath(xpath_config['block1'])
    id_list = []
    for b1 in block1:
        abstract = b1.xpath(xpath_config['abstract'])
        if abstract:
            doi = abstract[0].get('id')
            id_list.append(doi)
    return id_list


def fetch_arxiv_data(id_list):
    """使用 arxiv pypi 获取论文详细信息"""
    results = []
    client = arxiv.Client()
    search = arxiv.Search(id_list=id_list)
    for result in client.results(search):
        paper = {
            "doi": result.get_short_id(),
            "url": result.entry_id,
            "title": result.title.strip(),
            "authors": [a.name for a in result.authors],
            "subjects": [t for t in result.categories],
            "summary": result.summary.strip().replace('\n', ' ')
        }
        results.append(paper)
    return results


def main(url):
    check_and_create_table()
    check_and_create_user_table()
    r = redis.Redis(**REDIS_CONFIG)

    id_list = get_id_list(url)
    if not id_list:
        notice("No papers found on the page.")
        return 0

    papers = fetch_arxiv_data(id_list)

    new_papers = []
    for paper in papers:
        if save_or_skip_to_redis(r, paper):
            new_papers.append(paper)

    # 一次性写入 MySQL
    insert_mysql_bulk(new_papers)

    notice("Today's paper has been fetched successfully. Total %d new papers" % len(new_papers))
    return len(new_papers)


if __name__ == '__main__':
    result = main('https://arxiv.org/list/eess.SP/recent?skip=0&show=2000')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.inspection import inspect
import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
    "user": os.getenv("MYSQL_USER", "arxiv"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "arxiv"),
}

DATABASE_URL = f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}?charset=utf8mb4"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class BaseModel:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def to_dict(self, include_relations=False, seen=None):
        if seen is None:
            seen = set()

        identity = (self.__class__.__name__, getattr(self, "id", None))
        if identity in seen:
            return {"_ref": f"{identity[0]}:{identity[1]}"}
        seen.add(identity)

        result = {}
        mapper = inspect(self.__class__)

        for column in mapper.columns:
            if "password" in column.key:
                continue
            value = getattr(self, column.key)
            if column.key in ["authors", "subjects"]:
                value = value.split(",")
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            result[column.key] = value

        if include_relations:
            for rel in mapper.relationships:
                value = getattr(self, rel.key)
                if value is None:
                    result[rel.key] = None
                elif rel.uselist:
                    result[rel.key] = [v.to_dict(include_relations=False, seen=seen) for v in value]
                else:
                    result[rel.key] = value.to_dict(include_relations, seen)
        return result


Base = declarative_base(cls=BaseModel)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship
from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    marks = relationship("PaperMark", back_populates="user")


class Paper(Base):
    __tablename__ = "arxiv_papers"

    id = Column(Integer, primary_key=True, index=True)
    doi = Column(String(100), unique=True, nullable=False)
    url = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    authors = Column(Text, nullable=True)
    subjects = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    marks = relationship("PaperMark", back_populates="paper")


class PaperMark(Base):
    __tablename__ = "paper_marks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doi = Column(String(100), ForeignKey("arxiv_papers.doi"), nullable=False)

    is_favorite = Column(Boolean, default=False)  # 收藏
    rating = Column(Integer, nullable=True)  # 评分 (1~5)
    note = Column(Text, nullable=True)  # 笔记

    is_read = Column(Boolean, default=False)  # 已读
    is_uninterested = Column(Boolean, default=False)  # 不再想读/不感兴趣
    is_to_read = Column(Boolean, default=True)  # 想读/待读（默认新建时是待读）
    read_count = Column(Integer, default=0)  # 阅读次数
    progress = Column(Integer, default=0)  # 阅读进度 (0-100 表示百分比)

    first_read_at = Column(TIMESTAMP, nullable=True)  # 首次阅读时间
    last_read_at = Column(TIMESTAMP, nullable=True)  # 最后一次阅读时间
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="marks")
    paper = relationship("Paper", back_populates="marks")

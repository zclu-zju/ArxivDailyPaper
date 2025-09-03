from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import User, Paper, PaperMark
from auth_utils import get_password_hash, verify_password


def create_user(db: Session, username: str, password: str):
    user = User(username=username, password_hash=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def get_mark(db: Session, user_id: int, doi: str):
    return db.query(PaperMark).filter_by(user_id=user_id, doi=doi).first()


def get_papers(
        db: Session, skip: int = 0, limit: int = 20,
        search: str = None, subjects: str = None,
        user_id=None, include_marks=False,
        mark_filters: dict = None
):
    query = db.query(Paper)

    if search:
        like_str = f"%{search}%"
        query = query.filter(
            (Paper.title.like(like_str)) |
            (Paper.authors.like(like_str)) |
            (Paper.summary.like(like_str))
        )
    if subjects:
        query = query.filter(Paper.subjects.like(f"%{subjects}%"))

    if mark_filters and user_id:
        query = query.outerjoin(PaperMark, (Paper.doi == PaperMark.doi) & (PaperMark.user_id == user_id))

        for field, value in mark_filters.items():
            if hasattr(PaperMark, field) and value is not None:
                col = getattr(PaperMark, field)
                if field == "is_uninterested" and value is True:
                    query = query.filter(col == True)
                elif value is True:
                    query = query.filter(col == value)

    query = query.order_by(Paper.created_at.desc())

    length = query.count()
    result = query.offset(skip).limit(limit).all()

    items = []
    for paper in result:
        paper_dict = paper.to_dict(include_relations=include_marks and user_id)
        if paper_dict.get('marks', None):
            paper_dict['marks'] = paper_dict['marks'][0]
        items.append(paper_dict)

    return {
        "total": length,
        "items": items,
    }


def mark_paper(db: Session, user_id: int, doi: str, is_favorite: bool, note: str, rating: int):
    mark = db.query(PaperMark).filter_by(user_id=user_id, doi=doi).first()
    if mark:
        mark.is_favorite = is_favorite
        mark.note = note
        mark.rating = rating
    else:
        mark = PaperMark(user_id=user_id, doi=doi, is_favorite=is_favorite, note=note, rating=rating)
        db.add(mark)
    db.commit()
    return mark

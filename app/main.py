import os
from typing import Dict, Any

from fastapi import FastAPI, Depends, HTTPException, Query, Request, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import func

from jose import JWTError, jwt

from db import Base, engine, get_db
from schemas import *
from crud import *
from auth_utils import create_access_token, get_current_user, get_current_user_from_token

import arxiv

# 创建表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Arxiv Papers API", version="1.0", root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.middleware("http")
async def login_check_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)
    open_paths = ["/api/login", "/api/register", "/api/docs", "/api/redoc", "/api/openapi.json"]
    if not any(request.url.path.startswith(path) for path in open_paths):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
        token = auth.split(" ")[1]
        try:
            payload = get_current_user_from_token(token)
            request.state.user = payload  # 可以在后续路由里通过 request.state.user 获取用户信息
        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
    response = await call_next(request)
    return response


@app.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_username(db, req.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    create_user(db, req.username, req.password)
    return {"msg": "User registered successfully"}


@app.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(
        {"username": user.username, "id": user.id, "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S")})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


@app.get("/papers/")
def list_papers(
        page: int = 1,
        page_size: int = 20,
        search: str = Query(None),
        subjects: str = Query(None),
        marks: bool = Query(False),
        is_read: Optional[bool] = Query(None),
        is_favorite: Optional[bool] = Query(None),
        is_uninterested: Optional[bool] = Query(None),
        is_to_read: Optional[bool] = Query(None),
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size

    mark_filters = {}
    if is_read is not None:
        mark_filters["is_read"] = is_read
    if is_favorite is not None:
        mark_filters["is_favorite"] = is_favorite
    if is_uninterested is not None:
        mark_filters["is_uninterested"] = is_uninterested
    if is_to_read is not None:
        mark_filters["is_to_read"] = is_to_read

    papers = get_papers(
        db,
        skip=skip,
        limit=page_size,
        search=search,
        subjects=subjects,
        user_id=current_user['id'],
        include_marks=marks,
        mark_filters=mark_filters if mark_filters else None
    )
    return papers


@app.get("/papers/{doi}")
def get_paper_detail(
        doi: str,
        mark_as_read: bool = Query(True, description="是否自动标记为已读"),
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    paper = db.query(Paper).filter(Paper.doi == doi).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    if mark_as_read and current_user:
        mark = db.query(PaperMark).filter_by(doi=doi, user_id=current_user["id"]).first()
        if not mark:
            mark = PaperMark(
                doi=doi,
                user_id=current_user["id"],
                is_read=True,
                first_read_at=func.now(),
                last_read_at=func.now(),
                read_count=1
            )
            db.add(mark)
        else:
            if not mark.is_read:
                mark.is_read = True
                mark.first_read_at = mark.first_read_at or func.now()
            mark.last_read_at = func.now()
            mark.read_count = (mark.read_count or 0) + 1
        db.commit()
        db.refresh(mark)

    paper_dict = paper.to_dict()
    marks = paper.marks[0].to_dict()
    paper_dict["marks"] = marks
    return paper_dict


@app.patch("/marks/{doi}")
def update_or_create_mark(
        doi: str,
        field: str = Query(..., description="字段名"),
        value: str = Query(..., description="字段值"),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user),
):
    mark = db.query(PaperMark).filter_by(doi=doi, user_id=current_user["id"]).first()

    if not mark:
        mark = PaperMark(doi=doi, user_id=current_user["id"])
        db.add(mark)
        db.commit()
        db.refresh(mark)

    allowed_fields = {
        "is_favorite": bool,
        "note": str,
        "rating": int,
        "is_read": bool,
        "is_uninterested": bool,
        "is_to_read": bool,
        "read_count": int,
        "progress": int,
    }

    if field not in allowed_fields:
        raise HTTPException(status_code=400, detail="Invalid field")

    py_type = allowed_fields[field]
    try:
        if py_type == bool:
            cast_value = str(value).lower() in ["1", "true", "yes", "on"]
        else:
            cast_value = py_type(value)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid value type")

    setattr(mark, field, cast_value)
    db.commit()
    db.refresh(mark)

    return {"message": f"{field} updated", "new_value": cast_value, "id": mark.id}


@app.post("/marks/{doi}")
def update_or_create_mark_post(
        doi: str,
        field: str = Query(...),
        request_body: Dict[str, Any] = Body(...),
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user),
):
    mark = db.query(PaperMark).filter_by(doi=doi, user_id=current_user["id"]).first()
    if not mark:
        mark = PaperMark(doi=doi, user_id=current_user["id"])
        db.add(mark)
        db.commit()
        db.refresh(mark)

    allowed_fields = {
        "is_favorite": bool,
        "note": str,
        "rating": int,
        "is_read": bool,
        "is_uninterested": bool,
        "is_to_read": bool,
        "read_count": int,
        "progress": int,
    }

    if field not in allowed_fields:
        raise HTTPException(status_code=400, detail="Invalid field")

    value = request_body.get(field)
    if value is None:
        raise HTTPException(status_code=400, detail=f"Field '{field}' is required in request body")

    expected_type = allowed_fields[field]
    try:
        if expected_type == bool:
            if isinstance(value, str):
                cast_value = value.lower() in ["1", "true", "yes", "on"]
            else:
                cast_value = bool(value)
        else:
            cast_value = expected_type(value)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Cannot convert value to {expected_type.__name__}")

    setattr(mark, field, cast_value)
    db.commit()
    db.refresh(mark)

    return {
        "message": f"Field '{field}' updated successfully",
        "doi": doi,
        "field": field,
        "new_value": cast_value,
        "mark_id": mark.id,
    }


@app.get("/papers/user/{user_id}/favorites", response_model=List[PaperSchema])
def get_user_favorites(user_id: int, db: Session = Depends(get_db)):
    papers = (
        db.query(Paper)
        .join(PaperMark, Paper.doi == PaperMark.doi)
        .filter(PaperMark.user_id == user_id, PaperMark.is_favorite == True)
        .order_by(PaperMark.updated_at.desc())
        .all()
    )
    return [
        PaperSchema(
            doi=p.doi,
            url=p.url,
            title=p.title,
            authors=p.authors.split(",") if p.authors else [],
            subjects=p.subjects.split(",") if p.subjects else [],
            summary=p.summary,
        )
        for p in papers
    ]


# -------- 获取用户所有标记 --------
@app.get("/papers/user/{user_id}/marks", response_model=List[PaperSchema])
def get_user_marks(user_id: int, db: Session = Depends(get_db)):
    papers = (
        db.query(Paper)
        .join(PaperMark, Paper.doi == PaperMark.doi)
        .filter(PaperMark.user_id == user_id)
        .order_by(PaperMark.updated_at.desc())
        .all()
    )
    return [
        PaperSchema(
            doi=p.doi,
            url=p.url,
            title=p.title,
            authors=p.authors.split(",") if p.authors else [],
            subjects=p.subjects.split(",") if p.subjects else [],
            summary=p.summary,
        )
        for p in papers
    ]


@app.get("/papers/category/")
def get_papers_categories():
    run_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(run_dir, "subjects.txt"), "r") as f:
        subjects = [line.strip() for line in f.readlines()]
    return {"subjects": subjects}


# -------- 按学科获取 --------
@app.get("/papers/category/{category}", response_model=List[PaperSchema])
def get_papers_by_category(category: str, page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    papers = (
        db.query(Paper)
        .filter(Paper.subjects.like(f"%{category}%"))
        .order_by(Paper.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return [
        PaperSchema(
            doi=p.doi,
            url=p.url,
            title=p.title,
            authors=p.authors.split(",") if p.authors else [],
            subjects=p.subjects.split(",") if p.subjects else [],
            summary=p.summary,
        )
        for p in papers
    ]


# -------- 获取学科统计 --------
@app.get("/papers/category_counts/")
def get_category_counts(db: Session = Depends(get_db)):
    rows = db.query(Paper.subjects).all()
    counts: Dict[str, int] = {}
    for (subjects,) in rows:
        if not subjects:
            continue
        for subject in subjects.split(","):
            subject = subject.strip()
            counts[subject] = counts.get(subject, 0) + 1
    return counts


@app.get("/arxiv/search/", response_model=list[PaperBase])
def search_arxiv(query: str, max_results: int = 10):
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results)
    results = []
    for r in client.results(search):
        results.append(
            PaperBase(
                doi=r.get_short_id(),
                url=r.entry_id,
                title=r.title.strip(),
                authors=[a.name for a in r.authors],
                subjects=[t for t in r.categories],
                summary=r.summary.strip(),
            )
        )
    return results

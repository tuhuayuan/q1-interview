import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.concurrency import asynccontextmanager
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from q1.auth import JWTBearer, get_token
from q1.model import User
from q1.repo import Base, SessionLocal, get_repo, engine
from q1.schema import (
    AddScoreResponse,
    AddScoreRequest,
    GetScoreResponse,
    TokenReponse,
    TokenRequest,
)
from q1.redis import close_redis_pool, get_redis, init_redis_pool
from q1.service import UserCommandService, UserQueryService

# 加载环境变量
load_dotenv()

Base.metadata.create_all(bind=engine)

# 初始化日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis_pool()
    db = SessionLocal()
    try:
        if not db.query(User).first():
            # 初始化表数据
            db.add_all(
                [
                    User(user_id="admin", score=100, roles="admin"),
                    User(user_id="staff1", score=50, roles="staff"),
                ]
            )
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to initialize database: {e}")
    finally:
        db.close()
    yield
    await close_redis_pool()


app = FastAPI(lifespan=lifespan)


@app.post("/get_token", response_model=TokenReponse)
async def get_token_endpoint(request: TokenRequest, db: Session = Depends(get_repo)):
    # 加载用户
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {request.user_id} not found")

    return {"token": get_token(user)}


@app.get("/get_score", response_model=GetScoreResponse)
async def get_score_endpoint(
    db: Session = Depends(get_repo), token: dict = Depends(JWTBearer())
):
    user_id = token["user_id"]
    try:
        user_service = UserQueryService(db, get_redis())
        score = await user_service.read_score(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get score: {e}")

    return GetScoreResponse(user_id=user_id, score=score)


@app.post("/add_score", response_model=AddScoreResponse)
async def add_score_endpoint(
    request: AddScoreRequest,
    token: dict = Depends(JWTBearer()),
):
    user_id = token["user_id"]
    logger.info(
        f"Add {user_id} score: {request.score} modifier: {request.score_modifier}"
    )

    try:
        user_service = UserCommandService(get_redis())
        await user_service.add_score(user_id, request.score, request.score_modifier)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add score: {e}")

    return AddScoreResponse(user_id=user_id)

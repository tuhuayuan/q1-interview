from httpx import ASGITransport, AsyncClient
import pytest

from fastapi.testclient import TestClient
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from q1.auth import get_token
from q1.model import User
from q1.redis import close_redis_pool, get_redis, init_redis_pool
from q1.repo import Base, get_repo
from q1.service import UserQueryService
from q1_api import app

DATABASE_URL = "sqlite:///:memory:"

# 创建一个新的数据库引擎和会话工厂用于测试
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 覆盖应用的依赖
def override_get_repo():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_repo] = override_get_repo


# 创建测试客户端
@pytest_asyncio.fixture(scope="module")
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# 测试需要redis
@pytest_asyncio.fixture(scope="module")
async def setup_redis():
    await init_redis_pool("redis://localhost:6379/1")
    yield


# 测试需要一个临时数据库
@pytest_asyncio.fixture(scope="module")
def setup_database():
    # 创建测试数据库中的表
    Base.metadata.create_all(bind=engine)
    yield
    # 删除测试数据库中的表
    Base.metadata.drop_all(bind=engine)


def test_has_role_method():
    user = User(user_id="example", roles="admin;staff")
    assert user.has_role("admin") is True
    assert user.has_role("staff") is True
    assert user.has_role("user") is False


def get_token_for_user(user_id: str) -> str:
    with TestingSessionLocal() as db:
        user = db.query(User).filter(User.user_id == user_id).first()
        return get_token(user)


@pytest.mark.asyncio
async def test_add_score(async_client, setup_database, setup_redis):

    # 初始化数据库中的数据
    with TestingSessionLocal() as db:
        db.add_all(
            [
                User(user_id="admin", score=100, roles="admin"),
            ]
        )
        db.commit()

        query_service = UserQueryService(db, get_redis())
        await query_service.update_score("admin")

    # 获取JWTToken
    admin_token = get_token_for_user("admin")

    response = await async_client.get(
        "/get_score",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["score"] == 100

    # 加分
    response = await async_client.post(
        "/add_score",
        json={"user_id": "admin", "score": 10, "score_modifier": 2},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["user_id"] == "admin"

    # 这个时候读取应该没有变
    response = await async_client.get(
        "/get_score",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["score"] == 100

    # 模拟后台任务执行
    with TestingSessionLocal() as db:
        query_service = UserQueryService(db, get_redis())
        await query_service.update_score("admin")

    # 此时应该已经更新到位
    response = await async_client.get(
        "/get_score",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    assert response.json()["score"] == 120

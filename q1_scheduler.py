import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from q1.redis import init_redis_pool, close_redis_pool, get_redis
from q1.service import UserQueryService
from q1.model import User
from q1.repo import Base, engine, SessionLocal

Base.metadata.create_all(bind=engine)

# 初始化日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init():
    await init_redis_pool()


async def shutdown():
    await close_redis_pool()


async def update_all_scores():
    logger.info('updating all scores.')
    db = SessionLocal()
    try:
        service = UserQueryService(db, get_redis())
        # 获取所有用户ID
        user_ids = db.query(User.user_id).all()
        for user_id in user_ids:
            await service.update_score(user_id[0])
        logger.info(f'{len(user_ids)} scores updated.')
    finally:
        db.close()


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_all_scores, IntervalTrigger(seconds=5)
    )
    scheduler.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    start_scheduler()
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        loop.run_until_complete(shutdown())
        loop.stop()

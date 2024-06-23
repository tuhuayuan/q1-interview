import json
from redis import Redis
from sqlalchemy.orm import Session

from q1.model import User


class UserServiceError(Exception):
    def __init__(self, user_id: str, description: str):
        self.user_id = user_id
        self.description = description

    def __str__(self):
        return f"UserServiceError for user_id {self.user_id}: {self.description}"


class UserCommandService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def add_score(self, user_id: str, score: int = 0, score_modifier: int = 1):
        """将参数内容打包并推送到消息队列"""
        try:
            message = json.dumps(
                {"user_id": user_id, "score": score, "score_modifier": score_modifier}
            )
            await self.redis.lpush(f"score_queue:{user_id}", message)
        except Exception as e:
            raise UserServiceError(user_id, f"Failed to add score: {str(e)}")


class UserQueryService:
    def __init__(self, db: Session, redis: Redis):
        self.redis = redis
        self.db = db

    async def update_score(self, user_id: str):
        """更新用户分数"""
        try:
            user: User = self.db.query(User).filter(User.user_id == user_id).first()
        except Exception as e:
            raise UserServiceError(user_id, f"Failed get user {user_id}: {str(e)}")

        if not user:
            return

        # 获取队列中的所有累加请求
        queue_key = f"score_queue:{user_id}"

        try:
            messages = await self.redis.lrange(queue_key, 0, -1)
            await self.redis.ltrim(queue_key, len(messages), -1)
        except Exception as e:
            raise UserServiceError(
                user_id, f"Failed get user add_score messages: {str(e)}"
            )

        # 初始化当前分数
        current_score = user.score

        # 处理所有累加请求
        for message in messages:
            message_data = json.loads(message)
            if message_data["user_id"] == user_id:
                score = message_data["score"]
                score_modifier = message_data.get("score_modifier", 0)
                if user.has_role("admin"):
                    current_score += score * score_modifier
                else:
                    current_score += score

        try:
            # 更新数据库中的分数
            user.score = current_score
            self.db.commit()

            # 将更新后的分数写入Redis
            await self.redis.set(f"user:{user_id}:score", current_score)

        except:
            raise UserServiceError(user_id, f"Failed update user score: {str(e)}")

        return user

    async def read_score(self, user_id: str):
        """读取用户分数"""
        try:
            score = await self.redis.get(f"user:{user_id}:score")
        except Exception as e:
            raise UserServiceError(user_id, f"Failed to read score: {str(e)}")

        if score is None:
            score = 0
        else:
            score = int(score)
        return score

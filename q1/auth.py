from datetime import datetime

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from q1.model import User

TOKEN_KEY = "Insecure Key"


def get_token(user: User) -> str:
    """获取JWT令牌"""

    token = {"user_id": user.user_id}
    return jwt.encode(token, TOKEN_KEY, algorithm="HS256")


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials | None = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            payload = self.verify_jwt(credentials.credentials)
            if not payload:
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return payload
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> dict | None:
        try:
            payload = jwt.decode(jwtoken, TOKEN_KEY, algorithms=["HS256"])
        except:
            payload = None
        
        return payload

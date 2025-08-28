from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, Header, HTTPException, status, Security
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from uuid import UUID
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security_scheme),
    authorization: str = Header(None),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = None
    if (
        credentials
        and credentials.scheme.lower() == "bearer"
        and credentials.credentials
    ):
        token = credentials.credentials
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        org: str = payload.get("org")
        if user_id is None or org is None:
            raise credentials_exception
        user_uuid = UUID(user_id)
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User access forbidden",
        )

    return {"user": user, "org": org}

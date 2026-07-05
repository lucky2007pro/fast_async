from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from user.models import User, Blacklist
from user.security import (
    decode_token
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Tizimga kirish tasdiqlanmadi",
    )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception

    blacklisted = await db.execute(
        select(Blacklist).where(Blacklist.token == token)
    )
    if blacklisted.scalar_one_or_none() is not None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user


async def is_authenticated(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = decode_token(token)

    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Tizimga kirish tasdiqlanmadi",
    )

    if payload is None or payload.get("type") != "access":
        raise error

    # Blacklistda bor-yo'qligini tekshirish
    blacklisted = await db.execute(
        select(Blacklist).where(Blacklist.token == token)
    )
    if blacklisted.scalar_one_or_none() is not None:
        raise error

    user_id = payload.get("sub")
    if user_id is None:
        raise error

    user = await db.get(User, int(user_id))
    if user is None:
        raise error

    return True


async def delete_exp_tokens(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Blacklist).where(Blacklist.exp_time < datetime.now(timezone.utc)))
    expired_tokens = result.scalars().all()
    for token in expired_tokens:
        await db.delete(token)
    await db.commit()

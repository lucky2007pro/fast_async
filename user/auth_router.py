from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from user.permissions import get_current_user, is_authenticated

from db import get_db
from user.models import User, Blacklist
from user.schemas import UserCreate, Token, UserUpdate, PasswordChange, UserResponse
from user.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(
        select(User).where(
            (User.username == user_in.username) | (User.email == user_in.email)
        )
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu username yoki email allaqachon mavjud",
        )

    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password=hash_password(user_in.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"msg": 'User created', 
            'username':new_user.username}
    


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username yoki parol noto'g'ri",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Foydalanuvchi faol emas"
        )

    token_payload = {"sub": str(user.id)}
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str):
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token yaroqsiz yoki muddati o'tgan",
        )

    user_id = payload.get("sub")
    token_payload = {"sub": str(user_id)}
    new_access_token = create_access_token(token_payload)
    new_refresh_token = create_refresh_token(token_payload)

    return Token(access_token=new_access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/profile-update", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_update.username:
        result = await db.execute(select(User).where(User.username == user_update.username))
        existing_username = result.scalar_one_or_none()
        if existing_username and existing_username.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu username allaqachon mavjud")
        current_user.username = user_update.username
        
    if user_update.email:
        result = await db.execute(select(User).where(User.email == user_update.email))
        existing_email = result.scalar_one_or_none()
        if existing_email and existing_email.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu email allaqachon mavjud")
        current_user.email = user_update.email
        
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post("/password-change")
async def change_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(password_data.old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Joriy parol noto'g'ri"
        )
        
    current_user.password = hash_password(password_data.new_password)
    db.add(current_user)
    await db.commit()
    return {"msg": "Parol muvaffaqiyatli o'zgartirildi"}




@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(is_authenticated)
):
    payload = decode_token(token)

    type = payload.get("type")

    if type != "refresh" or type is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tizimga kirish tasdiqlanmadi",
        )
    
    exp = payload.get("exp")
    
    if exp is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tizimga kirish tasdiqlanmadi",
        )
    
    refresh_token = Blacklist(
        refresh=token,
        exp_time=exp,
    )
    db.add(refresh_token)
    await db.commit()
    await db.refresh(refresh_token)
    return {"msg": "Tizimdan chiqish muvaffaqiyatli amalga oshirildi"}
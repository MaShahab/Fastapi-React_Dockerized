from typing import List
from fastapi import APIRouter, Path, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from users import schemas
from users.schemas import UserLoginSchema, UserRegisterSchema
from users.models import UserModel, TokenModel
from sqlalchemy.orm import Session
from core.database import get_db
import secrets

router = APIRouter(tags=["users"], prefix="/users")


def generate_token(length=32):
    return secrets.token_hex(length)


@router.post("/register")
async def user_register(request: UserRegisterSchema, db: Session = Depends(get_db)):
    if db.query(UserModel).filter_by(username=request.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="username already exists"
        )
    user_obj = UserModel(username=request.username)
    user_obj.set_password(request.password)
    db.add(user_obj)
    db.commit()
    return JSONResponse(content={"detail": "user registered successfully"}, status_code=status.HTTP_201_CREATED)


@router.post("/login_token")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db)):
    user_obj = db.query(UserModel).filter_by(username=request.username).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="user doesnt exists"
        )
    if not user_obj.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="password is invalid"
        )
    token_obj = TokenModel(user_id=user_obj.id, token=generate_token())
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)
    return JSONResponse(
        content={"detail": "logged in successfully", "token": token_obj.token}
    )


from auth.jwt_auth import (
    generate_access_token,
    generate_refresh_token,
    get_authenticated_user,
    decode_refresh_token,
)

@router.post("/login")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db)):
    user_obj = db.query(UserModel).filter_by(username=request.username.lower()).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user doesnt exists"
        )
    if not user_obj.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="password is invalid"
        )

    access_token = generate_access_token(user_obj.id)
    refresh_token = generate_refresh_token(user_obj.id)
    return JSONResponse(
        content={
            "detail": "logged in successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


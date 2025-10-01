from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime as dt
from users.models import TokenModel, UserModel
from core.database import get_db
import secrets

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def generate_token(length):
    print(f"token is : {secrets.token_hex(length)}")
    return secrets.token_hex(length)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    db_token = db.query(TokenModel).filter(TokenModel.token == token).first()
    if not db_token or db_token.expiration < dt.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db.query(UserModel).filter(UserModel.id == db_token.user_id).first()

from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expires_at = datetime.utcnow() + expires_delta
    else:
        expires_at = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({'exp': expires_at})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 260000


def _env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} must be set")
    return value


def _secret_key() -> str:
    return _env("SECRET_KEY")


def _jwt_algorithm() -> str:
    algorithm = _env("JWT_ALGORITHM")
    if algorithm != "HS256":
        raise RuntimeError("Only HS256 is supported")
    return algorithm


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def _encode_jwt(payload: dict) -> str:
    algorithm = _jwt_algorithm()
    header = {"alg": algorithm, "typ": "JWT"}
    signing_input = ".".join(
        [
            _b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
            _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
        ]
    )
    signature = hmac.new(_secret_key().encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{_b64encode(signature)}"


def _decode_jwt(token: str) -> dict:
    algorithm = _jwt_algorithm()
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
        signing_input = f"{header_segment}.{payload_segment}"
        expected = hmac.new(_secret_key().encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
        received = _b64decode(signature_segment)
        if not hmac.compare_digest(expected, received):
            raise ValueError("Invalid signature")
        header = json.loads(_b64decode(header_segment))
        if header.get("alg") != algorithm:
            raise ValueError("Invalid algorithm")
        payload = json.loads(_b64decode(payload_segment))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("Token expired")
        return payload
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Invalid token") from None


def get_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    encoded = base64.b64encode(digest).decode("ascii")
    return f"{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${salt}${encoded}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, encoded = password_hash.split("$", 3)
        if algorithm != PBKDF2_ALGORITHM:
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        )
        expected = base64.b64decode(encoded.encode("ascii"))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(digest, expected)


def create_access_token(subject: uuid.UUID) -> str:
    minutes = int(_env("ACCESS_TOKEN_EXPIRE_MINUTES"))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {"sub": str(subject), "exp": int(expires_at.timestamp())}
    return _encode_jwt(payload)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = _decode_jwt(token)
        subject = payload.get("sub")
        user_id = uuid.UUID(subject)
    except (TypeError, ValueError):
        raise credentials_error from None

    user = db.get(User, user_id)
    if user is None:
        raise credentials_error
    return user

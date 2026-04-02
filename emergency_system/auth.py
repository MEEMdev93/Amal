"""
auth.py - نظام المصادقة JWT (بدون مكتبات خارجية - stdlib فقط)
"""
import hmac
import hashlib
import base64
import json
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_db, hash_password

SECRET_KEY = "hospital_emergency_secret_key_2024_madina_KSA_MOH"
ALGORITHM  = "HS256"
TOKEN_EXPIRE_HOURS = 8

security = HTTPBearer()

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    if padding != 4:
        s += '=' * padding
    return base64.urlsafe_b64decode(s)

def create_token(user_id: int, username: str, role: str) -> str:
    header  = {"alg": "HS256", "typ": "JWT"}
    exp_ts  = int((datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)).timestamp())
    iat_ts  = int(datetime.utcnow().timestamp())
    payload = {"sub": str(user_id), "username": username, "role": role,
               "exp": exp_ts, "iat": iat_ts}
    h_enc = _b64url_encode(json.dumps(header, separators=(',',':')).encode())
    p_enc = _b64url_encode(json.dumps(payload, separators=(',',':')).encode())
    signing_input = f"{h_enc}.{p_enc}".encode()
    sig = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    return f"{h_enc}.{p_enc}.{_b64url_encode(sig)}"

def decode_token(token: str) -> dict:
    parts = token.split('.')
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="رمز مصادقة غير صالح")
    h_enc, p_enc, sig_enc = parts
    signing_input = f"{h_enc}.{p_enc}".encode()
    expected_sig = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    try:
        actual_sig = _b64url_decode(sig_enc)
    except Exception:
        raise HTTPException(status_code=401, detail="رمز مصادقة غير صالح")
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise HTTPException(status_code=401, detail="رمز مصادقة غير صالح")
    try:
        payload = json.loads(_b64url_decode(p_enc))
    except Exception:
        raise HTTPException(status_code=401, detail="رمز مصادقة غير صالح")
    if payload.get("exp", 0) < int(datetime.utcnow().timestamp()):
        raise HTTPException(status_code=401, detail="انتهت صلاحية الجلسة، يرجى تسجيل الدخول مجدداً")
    return payload

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    payload = decode_token(credentials.credentials)
    conn = get_db()
    user = conn.execute(
        "SELECT id, username, full_name, role, active FROM users WHERE id=?",
        (int(payload["sub"]),)
    ).fetchone()
    conn.close()
    if not user or not user["active"]:
        raise HTTPException(status_code=401, detail="المستخدم غير نشط أو غير موجود")
    return dict(user)

def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="هذه العملية تتطلب صلاحيات المدير")
    return user

def require_operator(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] not in ("admin", "operator"):
        raise HTTPException(status_code=403, detail="هذه العملية تتطلب صلاحيات المشغّل")
    return user

def authenticate_user(username: str, password: str):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND active=1", (username,)
    ).fetchone()
    conn.close()
    if not user:
        return None
    if user["password_hash"] != hash_password(password):
        return None
    return dict(user)

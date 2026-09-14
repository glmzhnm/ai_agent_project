"""Пароли и JWT — код с высокой ценой ошибки, поэтому проверяется отдельно
от остального сервиса, без реальной БД."""

import time

import jwt
import pytest

from app.auth import decode_token, hash_password, issue_token, verify_password

SECRET = "test-secret"


def test_hash_and_verify_roundtrip():
    hashed = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", hashed)


def test_verify_rejects_wrong_password():
    hashed = hash_password("correct horse battery staple")
    assert not verify_password("wrong password", hashed)


def test_verify_rejects_garbage_hash_without_raising():
    assert not verify_password("anything", "not-a-bcrypt-hash")


def test_issue_and_decode_token_roundtrip():
    token = issue_token(user_id=42, login="ivan", secret=SECRET)
    payload = decode_token(token, SECRET)
    assert payload["user_id"] == 42
    assert payload["login"] == "ivan"


def test_decode_rejects_token_signed_with_other_secret():
    token = issue_token(user_id=1, login="ivan", secret="other-secret")
    with pytest.raises(jwt.PyJWTError):
        decode_token(token, SECRET)


def test_decode_rejects_expired_token():
    now = int(time.time())
    expired = jwt.encode(
        {"user_id": 1, "login": "ivan", "iat": now - 10, "exp": now - 5},
        SECRET,
        algorithm="HS256",
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(expired, SECRET)

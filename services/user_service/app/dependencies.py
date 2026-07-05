from fastapi import Request
from pwdlib import PasswordHash


def get_password_hash(request: Request) -> PasswordHash:
    return request.state.password_hash

from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import hashlib

from firebase.user_repo import create_user, get_user_by_username
from .schemas import UserLogin, UserRegister, ApiResponse, ErrorResponse

router = APIRouter()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/api/auth/register")
def register(user: UserRegister):
    user_data = create_user(user.username, hash_password(user.password))
    if not user_data:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(status="error", message="Tài khoản đã tồn tại", errors=[]).model_dump()
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=ApiResponse(status="success", message="Đăng ký thành công", data={"user_id": user_data["id"]}).model_dump()
    )

@router.post("/api/auth/login")
def login(user: UserLogin):
    user_data = get_user_by_username(user.username)
    if not user_data or user_data.get("password_hash") != hash_password(user.password):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(status="error", message="Sai tài khoản hoặc mật khẩu", errors=[]).model_dump()
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ApiResponse(status="success", message="Đăng nhập thành công", data={"user_id": user_data["id"]}).model_dump()
    )

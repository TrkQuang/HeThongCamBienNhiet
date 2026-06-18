import hashlib
from fastapi import APIRouter, status
from firebase.user_repo import create_user, get_user_by_username
from .schemas import UserLogin, UserRegister
from .utils import res_err, res_ok

router = APIRouter()

def hash_mat_khau(mat_khau: str) -> str:
    return hashlib.sha256(mat_khau.encode()).hexdigest()

@router.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    us = create_user(user.username, hash_mat_khau(user.password))
    if not us: return res_err("Tài khoản đã tồn tại", 400)
    return res_ok({"user_id": us["id"]}, "Đăng ký thành công", 201)

@router.post("/api/auth/login")
def login(user: UserLogin):
    us = get_user_by_username(user.username)
    if not us or us.get("password_hash") != hash_mat_khau(user.password):
        return res_err("Sai tài khoản hoặc mật khẩu", 401)
    return res_ok({"user_id": us["id"]}, "Đăng nhập thành công")
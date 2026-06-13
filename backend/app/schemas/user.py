from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


class RoleOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role_ids: List[int] = []

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[int]] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    roles: List[RoleOut] = []
    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_roles(cls, user):
        data = cls.model_validate({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "is_active": user.is_active,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "roles": [{"id": ur.role.id, "name": ur.role.name, "description": ur.role.description} for ur in user.roles if ur.role],
        })
        return data


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

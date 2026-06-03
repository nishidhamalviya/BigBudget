"""Authentication-related Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Payload for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    name: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"email": "user@example.com", "password": "securepass", "name": "Ravi"}]}}


class LoginRequest(BaseModel):
    """Payload for user login."""

    email: EmailStr
    password: str

    model_config = {"json_schema_extra": {"examples": [{"email": "user@example.com", "password": "securepass"}]}}


class TokenResponse(BaseModel):
    """JWT token returned on successful authentication."""

    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    """Request a password-reset link."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset a password using the one-time token."""

    token: str
    new_password: str = Field(..., min_length=8)


class MessageResponse(BaseModel):
    """Generic single-message response."""

    message: str

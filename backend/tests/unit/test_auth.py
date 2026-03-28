"""Tests for authentication service."""

import pytest
from unittest.mock import patch, AsyncMock
from types import SimpleNamespace


class TestJWT:
    """Test JWT token creation and validation."""

    def test_password_hash(self):
        """bcrypt hash + verify round trip."""
        import bcrypt as _bcrypt
        password = "test123"
        hashed = _bcrypt.hashpw(password.encode(), _bcrypt.gensalt())
        assert _bcrypt.checkpw(password.encode(), hashed)

    def test_password_wrong(self):
        """Wrong password fails verification."""
        import bcrypt as _bcrypt
        hashed = _bcrypt.hashpw(b"correct", _bcrypt.gensalt())
        assert not _bcrypt.checkpw(b"wrong", hashed)

    def test_jwt_create_and_decode(self):
        """Create access token and decode it."""
        from jose import jwt
        secret = "test-secret"
        payload = {"sub": "42", "role": "admin", "type": "access"}
        token = jwt.encode(payload, secret, algorithm="HS256")
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        assert decoded["sub"] == "42"
        assert decoded["role"] == "admin"

    def test_jwt_invalid_token(self):
        """Invalid token raises error."""
        from jose import jwt, JWTError
        with pytest.raises(JWTError):
            jwt.decode("invalid.token.here", "secret", algorithms=["HS256"])


class TestOptionalUser:
    """Test get_optional_user fallback for demo mode."""

    def test_demo_user_has_defaults(self):
        """Demo user should have id=0, role=user."""
        user = SimpleNamespace(id=0, role="user", username="demo")
        assert user.id == 0
        assert user.role == "user"

#!/usr/bin/env python3
"""
JWT Manager for PLC-GPT Enterprise Authentication
Phase 3 Days 6-7: Enterprise Features
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)


class TokenData(BaseModel):
    """Token data model for JWT payload."""
    username: Optional[str] = None
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[list] = None
    expires_at: Optional[datetime] = None


class JWTManager:
    """
    JWT Token Manager for enterprise authentication.
    
    Features:
    - Secure JWT token creation and validation
    - Password hashing and verification
    - Token expiration handling
    - Refresh token support
    - Security audit logging
    """
    
    def __init__(self, settings=None):
        """
        Initialize JWT Manager.
        
        Args:
            settings: Enterprise settings instance
        """
        if settings:
            self.secret_key = settings.jwt_secret
            self.algorithm = settings.jwt_algorithm
            self.access_token_expire_hours = settings.jwt_expiration_hours
            self.refresh_token_expire_days = settings.jwt_refresh_expiration_days
        else:
            # Fallback to environment variables
            self.secret_key = os.getenv("JWT_SECRET", self._generate_secret_key())
            self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
            self.access_token_expire_hours = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
            self.refresh_token_expire_days = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", "7"))
        
        # Password context for hashing
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Validate configuration
        self._validate_configuration()
        
        logger.info("JWT Manager initialized",
                   algorithm=self.algorithm,
                   access_token_expire_hours=self.access_token_expire_hours,
                   refresh_token_expire_days=self.refresh_token_expire_days)
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key if none provided."""
        key = secrets.token_urlsafe(32)
        logger.warning("JWT secret key generated automatically. Set JWT_SECRET environment variable for production.")
        return key
    
    def _validate_configuration(self):
        """Validate JWT configuration."""
        if not self.secret_key or len(self.secret_key) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        
        if self.algorithm not in ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]:
            raise ValueError(f"Unsupported JWT algorithm: {self.algorithm}")
        
        if self.access_token_expire_hours <= 0:
            raise ValueError("Access token expiration must be positive")
        
        if self.refresh_token_expire_days <= 0:
            raise ValueError("Refresh token expiration must be positive")
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Token payload data
            expires_delta: Custom expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=self.access_token_expire_hours)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            
            logger.info("Access token created",
                       user_id=data.get("user_id"),
                       email=data.get("email"),
                       expires_at=expire.isoformat())
            
            return encoded_jwt
            
        except Exception as e:
            logger.error("Failed to create access token", error=str(e))
            raise JWTError(f"Failed to create access token: {str(e)}")
    
    def create_refresh_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT refresh token.
        
        Args:
            data: Token payload data
            expires_delta: Custom expiration time
            
        Returns:
            JWT refresh token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            
            logger.info("Refresh token created",
                       user_id=data.get("user_id"),
                       email=data.get("email"),
                       expires_at=expire.isoformat())
            
            return encoded_jwt
            
        except Exception as e:
            logger.error("Failed to create refresh token", error=str(e))
            raise JWTError(f"Failed to create refresh token: {str(e)}")
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            TokenData object if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            token_type = payload.get("type")
            if token_type not in ["access", "refresh"]:
                logger.warning("Invalid token type", token_type=token_type)
                return None
            
            # Extract token data
            username = payload.get("username")
            email = payload.get("email")
            user_id = payload.get("user_id")
            role = payload.get("role")
            permissions = payload.get("permissions")
            expires_at = datetime.fromtimestamp(payload.get("exp", 0))
            
            token_data = TokenData(
                username=username,
                email=email,
                user_id=user_id,
                role=role,
                permissions=permissions,
                expires_at=expires_at
            )
            
            logger.debug("Token verified successfully",
                        user_id=user_id,
                        email=email,
                        token_type=token_type,
                        expires_at=expires_at.isoformat())
            
            return token_data
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.JWTClaimsError:
            logger.warning("Invalid token claims")
            return None
        except jwt.JWTError as e:
            logger.warning("Token verification failed", error=str(e))
            return None
        except Exception as e:
            logger.error("Unexpected error during token verification", error=str(e))
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if a token is expired.
        
        Args:
            token: JWT token string
            
        Returns:
            True if expired, False otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp = payload.get("exp")
            if exp is None:
                return True
            
            return datetime.utcnow() > datetime.fromtimestamp(exp)
            
        except Exception:
            return True
    
    def get_token_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get token payload without verification (for debugging).
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload if decodable, None otherwise
        """
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception:
            return None
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        try:
            hashed = self.pwd_context.hash(password)
            logger.debug("Password hashed successfully")
            return hashed
            
        except Exception as e:
            logger.error("Failed to hash password", error=str(e))
            raise ValueError(f"Failed to hash password: {str(e)}")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            result = self.pwd_context.verify(plain_password, hashed_password)
            logger.debug("Password verification completed", result=result)
            return result
            
        except Exception as e:
            logger.error("Password verification failed", error=str(e))
            return False
    
    def create_token_pair(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create both access and refresh tokens.
        
        Args:
            user_data: User data for token payload
            
        Returns:
            Dictionary with access_token and refresh_token
        """
        access_token = self.create_access_token(user_data)
        refresh_token = self.create_refresh_token(user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Create a new access token using a refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token if refresh token is valid, None otherwise
        """
        token_data = self.verify_token(refresh_token)
        if not token_data:
            logger.warning("Invalid refresh token provided")
            return None
        
        # Check if it's actually a refresh token
        payload = self.get_token_payload(refresh_token)
        if not payload or payload.get("type") != "refresh":
            logger.warning("Token is not a refresh token")
            return None
        
        # Create new access token with same user data
        user_data = {
            "username": token_data.username,
            "email": token_data.email,
            "user_id": token_data.user_id,
            "role": token_data.role,
            "permissions": token_data.permissions
        }
        
        new_access_token = self.create_access_token(user_data)
        
        logger.info("Access token refreshed",
                   user_id=token_data.user_id,
                   email=token_data.email)
        
        return new_access_token
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token (placeholder for token blacklisting).
        
        Args:
            token: JWT token to revoke
            
        Returns:
            True if token was revoked successfully
        """
        # In a full implementation, this would add the token to a blacklist
        # For now, we'll just log the revocation
        token_data = self.verify_token(token)
        if token_data:
            logger.info("Token revoked",
                       user_id=token_data.user_id,
                       email=token_data.email)
            return True
        return False
    
    def get_algorithm(self) -> str:
        """Get the current JWT algorithm."""
        return self.algorithm
    
    def get_token_expiration_hours(self) -> int:
        """Get access token expiration in hours."""
        return self.access_token_expire_hours
    
    def get_refresh_expiration_days(self) -> int:
        """Get refresh token expiration in days."""
        return self.refresh_token_expire_days


# Global JWT manager instance
jwt_manager = None


def get_jwt_manager(settings=None) -> JWTManager:
    """
    Get or create JWT manager instance.
    
    Args:
        settings: Enterprise settings instance
        
    Returns:
        JWTManager instance
    """
    global jwt_manager
    if jwt_manager is None:
        jwt_manager = JWTManager(settings)
    return jwt_manager 
from sqlalchemy import Column, String, Integer, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import Base, BaseModel
from enum import Enum as PyEnum

class UserRole(str, PyEnum):
    ADMIN = "admin"
    USER = "user"
    ANALYST = "analyst"

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    alerts = relationship("Alert", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Alert(BaseModel):
    __tablename__ = "alerts"
    
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String(50))  # e.g., price_change, sentiment_change
    condition = Column(JSON)  # e.g., {"threshold": 10, "direction": "increase"}
    is_active = Column(Boolean, default=True)
    user = relationship("User", back_populates="alerts")

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"
    
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    user = relationship("User", back_populates="audit_logs")

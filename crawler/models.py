from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, ForeignKey, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
import os
from datetime import datetime

Base = declarative_base()

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign key to organisation
    organisation_id = Column(Integer, ForeignKey('organisations.id'), nullable=False)
    organisation = relationship("Organisation", back_populates="users")
    
    # Many-to-many relationship with roles
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    
    # One-to-many relationship with API keys
    api_keys = relationship("ApiKey", back_populates="user")

class Organisation(Base):
    __tablename__ = 'organisations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=True)
    plan = Column(String(50), nullable=False, default='FREE')
    remaining_scans_month = Column(Integer, nullable=False, default=0)
    # Integration settings
    slack_webhook_url = Column(String(500), nullable=True)
    resend_api_key = Column(String(255), nullable=True)
    notification_email = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # One-to-many relationship with users
    users = relationship("User", back_populates="organisation")

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # 'owner', 'admin', 'viewer'
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Many-to-many relationship with users
    users = relationship("User", secondary=user_roles, back_populates="roles")

class ApiKey(Base):
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(64), unique=True, nullable=False)  # SHA-256 hash
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="api_keys")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/regulaai")

def get_engine():
    return create_engine(DATABASE_URL)

def get_session_local():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

SessionLocal = get_session_local()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
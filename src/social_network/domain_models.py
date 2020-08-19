from enum import Enum as BuiltinEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Enum
from sqlalchemy import DateTime
from sqlalchemy import Date



Base = declarative_base()



class SecurityRoles(str, BuiltinEnum):
    admin = "admin"
    user = "user"


class Sex(str, BuiltinEnum):
    male = "MALE"
    female = "FEMALE"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(250), nullable=False)
    security_role = Column(Enum(SecurityRoles), default=SecurityRoles.user, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    
    profile = relationship("UserProfile", uselist=False, back_populates="user_cred")


class UserProfile(Base):
    __tablename__ = "users_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    first_name = Column(String(250), nullable=False)
    last_name = Column(String(250), nullable=False)
    full_name = Column(String(250), nullable=False)
    sex = Column(Enum(Sex), nullable=True)
    country = Column(String(250), nullable=True)
    city = Column(String(250), nullable=True)
    birthday = Column(Date, nullable=True)
    phone = Column(String(25), nullable=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    user_cred = relationship("User", back_populates="profile")
    posts = relationship("Post", back_populates="user_profile")
    likes = relationship("Like", back_populates="user_profile")


class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users_profiles.id'), nullable=False)
    title = Column(String(250), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    user_profile = relationship("UserProfile", back_populates="posts")
    likes = relationship("Like", back_populates="post")
    


class Like(Base):
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users_profiles.id'), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

    post = relationship("Post", back_populates="likes")
    user_profile = relationship("UserProfile", back_populates="likes")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(250), unique=True, nullable=False)
    exp = Column(DateTime, nullable=False)
    os = Column(String(250), nullable=False)
    device = Column(String(250), nullable=False)
    browser = Column(String(250), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

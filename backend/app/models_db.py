# Purpose: ORM models (User, Trip, RagDoc)
from __future__ import annotations                                     # Enable forward refs without quotes

from datetime import datetime                                          # Correct Python type for DateTime
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class User(Base):
    """User account with hashed password."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    trips: Mapped[list[Trip]] = relationship(back_populates="user", cascade="all,delete")


class Trip(Base):
    """Saved itinerary per user."""
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    itinerary: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user: Mapped[User] = relationship(back_populates="trips")


class RagDoc(Base):
    """Local knowledge document (for RAG) with light metadata."""
    __tablename__ = "rag_docs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    city: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

"""Persistence models for the single-user demo."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base

JsonType = JSON().with_variant(JSONB(), "postgresql")


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    rules: Mapped[list[Rule]] = relationship(cascade="all, delete-orphan", back_populates="project")
    test_sets: Mapped[list[TestSet]] = relationship(cascade="all, delete-orphan", back_populates="project")
    reports: Mapped[list[AnalysisReport]] = relationship(cascade="all, delete-orphan", back_populates="project")


class Rule(Base):
    __tablename__ = "rules"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(30))
    definition: Mapped[dict[str, Any]] = mapped_column(JsonType)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    project: Mapped[Project] = relationship(back_populates="rules")


class TestSet(Base):
    __tablename__ = "test_sets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))
    strings: Mapped[list[dict[str, Any]]] = mapped_column(JsonType)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    project: Mapped[Project] = relationship(back_populates="test_sets")


class AnalysisReport(Base):
    __tablename__ = "analysis_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(String(100))
    input_refs: Mapped[dict[str, Any]] = mapped_column(JsonType)
    result: Mapped[dict[str, Any]] = mapped_column(JsonType)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    project: Mapped[Project] = relationship(back_populates="reports")

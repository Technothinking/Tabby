import uuid
from typing import Any, Dict, Optional
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    goal_template: Mapped[str] = mapped_column(Text, nullable=False)
    constraints_schema: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    is_eval_task: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
class Run(Base):
    __tablename__ = "runs"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    constraints: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(Text, default="pending", index=True)
    mode: Mapped[str] = mapped_column(Text, default="live")
    max_steps: Mapped[int] = mapped_column(Integer, default=40)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    final_status_reason: Mapped[Optional[str]] = mapped_column(Text)
    
    steps = relationship("Step", back_populates="run", cascade="all, delete-orphan")

class Step(Base):
    __tablename__ = "steps"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    node_name: Mapped[str] = mapped_column(Text, nullable=False)
    observation_ref: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    proposed_action: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    guardrail_decision: Mapped[Optional[str]] = mapped_column(Text)
    action_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    verification_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer)
    token_cost: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    run = relationship("Run", back_populates="steps")
    approvals = relationship("Approval", back_populates="step", cascade="all, delete-orphan")

class Approval(Base):
    __tablename__ = "approvals"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    step_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("steps.id", ondelete="CASCADE"))
    requested_action_summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, default="pending")
    decided_by: Mapped[Optional[str]] = mapped_column(Text)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    step = relationship("Step", back_populates="approvals")

class TraceSummary(Base):
    __tablename__ = "trace_summaries"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id"))
    domain: Mapped[str] = mapped_column(Text, nullable=False)
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    strategy_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    outcome: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class TraceEmbedding(Base):
    __tablename__ = "trace_embeddings"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    trace_summary_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trace_summaries.id", ondelete="CASCADE"))
    embedding = mapped_column(Vector(3072), nullable=False)

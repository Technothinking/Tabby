import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.db.models import Run, Step, Approval
from app.api.schemas import RunCreate, RunResponse, ApprovalRequestPayload
from fastapi import BackgroundTasks
from app.api.worker import execute_run_task

router = APIRouter()

@router.post("", response_model=RunResponse, status_code=201)
async def create_run(run_in: RunCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    run = Run(
        goal=run_in.goal,
        task_id=run_in.task_id,
        constraints=run_in.constraints,
        mode=run_in.mode,
        max_steps=run_in.max_steps,
        status="pending"
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    
    background_tasks.add_task(execute_run_task, run.id, run.goal)
    
    # Minimal response, async worker orchestration will be wired next
    # Return as dict to prevent Pydantic from triggering lazy-loads on relationship `steps`.
    return {
        "id": run.id,
        "goal": run.goal,
        "status": run.status,
        "steps": []
    }

@router.get("", response_model=List[RunResponse])
async def list_runs(db: AsyncSession = Depends(get_db), limit: int = 20, offset: int = 0):
    result = await db.execute(
        select(Run)
        .options(selectinload(Run.steps))
        .order_by(Run.started_at.desc())
        .limit(limit)
        .offset(offset)
    )
    runs = result.scalars().all()
    return runs

@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Run).options(selectinload(Run.steps)).where(Run.id == run_id)
    )
    run = result.scalars().first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@router.post("/{run_id}/approvals/{approval_id}")
async def resolve_approval(
    run_id: uuid.UUID, 
    approval_id: uuid.UUID, 
    payload: ApprovalRequestPayload, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Approval).where(Approval.id == approval_id, Approval.step.has(run_id=run_id)))
    approval = result.scalars().first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    approval.status = payload.decision
    approval.decided_by = payload.decided_by
    await db.commit()
    
    # Future: Signal LangGraph WS checkpointer to resume the process
    return {"message": "Approval processed successfully", "status": payload.decision}

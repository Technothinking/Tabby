from app.db.session import async_session

from app.db.models import TraceSummary, TraceEmbedding
import uuid

class MemoryWriter:
    @staticmethod
    async def persist_trace(run_id: str, summary_dict: dict, embedding: list[float]):
        async with async_session() as session:
            try:
                trace_id = uuid.uuid4()
                # Create summary record
                trace_summary = TraceSummary(
                    id=trace_id,
                    run_id=uuid.UUID(run_id),
                    domain=summary_dict.get("domain", "unknown"),
                    summary_text=f"Summary for {summary_dict.get('goal_category', 'task')}",
                    strategy_json=summary_dict.get("strategy_json", {}),
                    outcome=summary_dict.get("outcome", "failure")
                )
                
                # Create embedding record
                trace_embedding = TraceEmbedding(
                    trace_summary_id=trace_id,
                    embedding=embedding
                )
                
                session.add(trace_summary)
                await session.flush()
                session.add(trace_embedding)
                await session.commit()
            except Exception as e:
                print(f"Failed to persist memory trace: {e}")

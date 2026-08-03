from app.db.session import async_session

from sqlalchemy import text
from app.agent.memory.embeddings import Embedder
import json

class MemoryRetriever:
    @staticmethod
    async def retrieve_hints(goal: str, domain_hint: str = "", top_k: int = 3) -> list[dict]:
        vector = await Embedder.embed_query(goal, domain_hint)
        vector_str = f"[{','.join(map(str, vector))}]"
        
        async with async_session() as session:
            sql = text("""
                SELECT ts.domain, ts.summary_text, ts.strategy_json, ts.outcome,
                       te.embedding <-> :vec AS distance
                FROM trace_summaries ts
                JOIN trace_embeddings te ON ts.id = te.trace_summary_id
                ORDER BY distance ASC
                LIMIT :limit
            """)
            
            result = await session.execute(sql, {"vec": vector_str, "limit": top_k})
            rows = result.fetchall()
            
            hints = []
            for row in rows:
                hints.append({
                    "domain": row.domain,
                    "strategy": row.strategy_json,
                    "outcome": row.outcome
                })
            return hints
